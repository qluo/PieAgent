"""Independent context-selection and model-message conversion stages."""

from collections.abc import Callable, Sequence

from pie_ai import ModelMessage

from .messages import AgentMessage
from .state import AgentState


TransformContext = Callable[
    [Sequence[AgentMessage], AgentState],
    list[AgentMessage],
]
ConvertToModelMessages = Callable[
    [Sequence[AgentMessage]],
    list[ModelMessage],
]


class Context:
    """Provide compatible defaults for both context-boundary stages."""

    def __init__(self, system_prompt: str = "") -> None:
        self.system_prompt = system_prompt.strip()

    def transform_context(
        self,
        messages: Sequence[AgentMessage],
        state: AgentState,
    ) -> list[AgentMessage]:
        """Select the agent messages to expose to the conversion stage."""
        del state
        return list(messages)

    def convert_to_model_messages(
        self, messages: Sequence[AgentMessage]
    ) -> list[ModelMessage]:
        """Convert prepared messages without provider-specific behavior."""
        model_messages: list[ModelMessage] = []
        if self.system_prompt:
            model_messages.append(ModelMessage(role="system", content=self.system_prompt))

        for message in messages:
            if message.kind == "agent_note":
                model_messages.append(
                    ModelMessage(
                        role="system",
                        content=f"Context note (not instructions):\n{message.content}",
                    )
                )
            else:
                model_messages.append(
                    ModelMessage(
                        role=message.kind,
                        content=message.content,
                        tool_calls=message.tool_calls,
                        tool_name=message.tool_name,
                    )
                )
        return model_messages

    # Compatibility aliases for callers using the original Context API.
    def transform(
        self,
        messages: Sequence[AgentMessage],
        state: AgentState,
    ) -> list[AgentMessage]:
        return self.transform_context(messages, state)

    def to_model_messages(
        self, messages: Sequence[AgentMessage]
    ) -> list[ModelMessage]:
        return self.convert_to_model_messages(messages)
