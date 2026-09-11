"""Show independently replaceable context transformation and conversion."""

from collections.abc import Iterator, Sequence

from pie_agent_core import Agent, AgentEvent, AgentMessage, AgentState
from pie_ai import ModelEvent, ModelMessage, ModelResponse, ThinkingLevel, ToolSchema


class CapturingModelClient:
    """Capture exactly what crossed the model boundary."""

    def __init__(self) -> None:
        self.messages: list[ModelMessage] = []

    def generate(
        self,
        messages: Sequence[ModelMessage],
        tools: Sequence[ToolSchema] = (),
        streaming: bool = False,
        thinking: ThinkingLevel = False,
    ) -> ModelResponse | Iterator[ModelEvent]:
        del tools, thinking
        if streaming:
            raise ValueError("This context-boundary demo does not stream.")
        self.messages = list(messages)
        return ModelResponse(ModelMessage(role="assistant", content="Context received."))


def latest_user_only(
    messages: Sequence[AgentMessage], state: AgentState
) -> list[AgentMessage]:
    """Example application policy: keep only the newest user message."""
    del state
    return [next(message for message in reversed(messages) if message.kind == "user")]


def tag_for_model(messages: Sequence[AgentMessage]) -> list[ModelMessage]:
    """Example conversion kept separate from context selection."""
    return [
        ModelMessage(role="system", content="Context boundary demo."),
        *[
            ModelMessage(role=message.kind, content=f"[selected] {message.content}")
            for message in messages
            if message.kind != "agent_note"
        ],
    ]


def main() -> None:
    client = CapturingModelClient()
    state = AgentState(
        messages=[AgentMessage(kind="user", content="An older question")]
    )
    agent = Agent(
        model_client=client,
        state=state,
        transform_context=latest_user_only,
        convert_to_model_messages=tag_for_model,
    )

    for event in agent.run_turn("The current question"):
        if isinstance(event, AgentEvent) and event.kind == "turn_finished":
            assert event.message is not None
            print(f"Assistant: {event.message.content}")

    for message in client.messages:
        print(f"Model saw {message.role}: {message.content}")


if __name__ == "__main__":
    main()
