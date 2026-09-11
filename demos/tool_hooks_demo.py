"""Exercise async policy and result hooks around sequential agent tools."""

import asyncio
from collections.abc import Iterator, Sequence

from pie_agent_core import (
    Agent,
    AgentEvent,
    AgentTool,
    AgentToolResult,
    ToolCallContext,
    ToolCallDecision,
    ToolExecutionContext,
)
from pie_ai import (
    ModelEvent,
    ModelMessage,
    ModelResponse,
    ThinkingLevel,
    ToolCall,
    ToolSchema,
)


class RecordingTool(AgentTool):
    def __init__(self, name: str, executions: list[str], fails: bool = False) -> None:
        super().__init__(name, f"Demo {name} tool.", {"type": "object"})
        self.executions = executions
        self.fails = fails

    def execute(self, arguments: dict[str, object]) -> AgentToolResult:
        self.executions.append(f"{self.name}:{arguments.get('value', '')}")
        if self.fails:
            raise RuntimeError("private backend detail")
        return AgentToolResult(
            f"value={arguments['value']}; token=demo-secret",
        )


class HookDemoModelClient:
    def generate(
        self,
        messages: Sequence[ModelMessage],
        tools: Sequence[ToolSchema] = (),
        streaming: bool = False,
        thinking: ThinkingLevel = False,
    ) -> ModelResponse | Iterator[ModelEvent]:
        del tools, thinking
        if streaming:
            raise ValueError("This deterministic demo does not stream.")

        results = [message for message in messages if message.role == "tool_result"]
        if not results:
            return ModelResponse(
                ModelMessage(
                    role="assistant",
                    tool_calls=[
                        ToolCall("echo", {"value": "original"}, "call-1"),
                        ToolCall("blocked", {"value": "unsafe"}, "call-2"),
                        ToolCall("explode", {"value": "boom"}, "call-3"),
                    ],
                )
            )
        return ModelResponse(
            ModelMessage(
                role="assistant",
                content=" | ".join(message.content for message in results),
            )
        )


async def main_async() -> None:
    executions: list[str] = []
    hook_order: list[str] = []
    observations: list[str] = []
    caller_loop_gate = asyncio.Event()

    async def release_gate() -> None:
        await asyncio.sleep(0)
        caller_loop_gate.set()

    asyncio.create_task(release_gate())

    async def before_tool_call(context: ToolCallContext) -> ToolCallDecision:
        # This loop-bound Event proves the hook runs on the caller's loop.
        await caller_loop_gate.wait()
        hook_order.append(f"before:{context.tool_name}")
        if context.tool_name == "echo":
            return ToolCallDecision.approve({"value": "adjusted"})
        if context.tool_name == "blocked":
            return ToolCallDecision.reject("Declined by demo policy.")
        return ToolCallDecision.approve()

    async def after_tool_call(context: ToolExecutionContext) -> AgentToolResult:
        await asyncio.sleep(0)
        hook_order.append(f"after:{context.call.tool_name}")
        observations.append(
            f"{context.call.tool_name}:{context.result.status}:"
            f"executed={context.executed}:error={context.exception is not None}"
        )
        if context.call.tool_name == "echo":
            return AgentToolResult("NORMALIZED value=adjusted; token=[REDACTED]")
        if context.result.status == "error":
            return AgentToolResult(
                f"NORMALIZED ERROR: {context.call.tool_name} failed", "error"
            )
        return context.result

    agent = Agent(
        model_client=HookDemoModelClient(),
        tools=[
            RecordingTool("echo", executions),
            RecordingTool("blocked", executions),
            RecordingTool("explode", executions, fails=True),
        ],
        before_tool_call=before_tool_call,
        after_tool_call=after_tool_call,
    )

    final_text = ""
    async for event in agent.run_turn_async("run the hook demo"):
        if isinstance(event, AgentEvent) and event.kind == "turn_finished":
            assert event.message is not None
            final_text = event.message.content

    assert executions == ["echo:adjusted", "explode:boom"]
    assert hook_order == [
        "before:echo",
        "after:echo",
        "before:blocked",
        "after:blocked",
        "before:explode",
        "after:explode",
    ]
    assert "demo-secret" not in final_text
    assert "private backend detail" not in final_text
    assert "NORMALIZED value=adjusted; token=[REDACTED]" in final_text
    assert "Declined by demo policy." in final_text
    assert "NORMALIZED ERROR: explode failed" in final_text

    print("Executions:", " -> ".join(executions))
    print("Hooks:", " -> ".join(hook_order))
    print("Observed:", " | ".join(observations))
    print("Assistant:", final_text)


def main() -> None:
    # The native async turn API keeps loop-bound hook resources on this loop.
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
