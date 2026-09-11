"""Run the generic text agent without Ollama or the voice application."""

import argparse
from collections.abc import Iterator, Sequence

from pie_agent_core import Agent, AgentEvent, AgentTool, AgentToolResult
from pie_ai import (
    ModelEvent,
    ModelMessage,
    ModelResponse,
    ThinkingLevel,
    ToolCall,
    ToolSchema,
)


class DemoTool(AgentTool):
    """Record execution so the demo can display sequential tool ordering."""

    def __init__(self, name: str, execution_order: list[str]) -> None:
        super().__init__(
            name=name,
            description=f"Apply the demo {name} operation.",
            parameters={"type": "object", "properties": {}},
        )
        self.execution_order = execution_order

    def execute(self, arguments: dict[str, object]) -> AgentToolResult:
        self.execution_order.append(self.name)
        return AgentToolResult(content=f"{self.name} completed for {arguments['text']}")


class DemoModelClient:
    """Return one tool request followed by one complete text response."""

    def generate(
        self,
        messages: Sequence[ModelMessage],
        tools: Sequence[ToolSchema] = (),
        streaming: bool = False,
        thinking: ThinkingLevel = False,
    ) -> ModelResponse | Iterator[ModelEvent]:
        del tools, thinking
        if streaming:
            raise ValueError("This complete-response demo does not stream.")

        tool_results = [
            message for message in messages if message.role == "tool_result"
        ]
        if not tool_results:
            prompt = next(
                message.content for message in reversed(messages) if message.role == "user"
            )
            return ModelResponse(
                ModelMessage(
                    role="assistant",
                    tool_calls=[
                        ToolCall(name="first", arguments={"text": prompt}),
                        ToolCall(name="second", arguments={"text": prompt}),
                    ],
                )
            )

        return ModelResponse(
            ModelMessage(
                role="assistant",
                content="Both tools finished: "
                + "; ".join(message.content for message in tool_results),
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="?", default="hello")
    args = parser.parse_args()

    execution_order: list[str] = []
    agent = Agent(
        model_client=DemoModelClient(),
        tools=[
            DemoTool("first", execution_order),
            DemoTool("second", execution_order),
        ],
    )

    final_text = ""
    for event in agent.run_turn(args.prompt):
        if isinstance(event, AgentEvent) and event.kind == "turn_finished":
            assert event.message is not None
            final_text = event.message.content

    print(f"Tool order: {' -> '.join(execution_order)}")
    print(f"Assistant: {final_text}")


if __name__ == "__main__":
    main()
