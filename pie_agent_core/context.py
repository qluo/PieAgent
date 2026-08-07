"""Convert agent conversation entries into model-visible messages."""

from collections.abc import Sequence

from pie_ai import ModelMessage

from .conversation import AgentConversation
from .messages import AgentMessage


class Context:
    """Own generic prompt preparation and model-message conversion."""

    def __init__(self, system_prompt: str = "") -> None:
        self.system_prompt = system_prompt.strip()

    def transform(
        self,
        messages: Sequence[AgentMessage],
        conversation: AgentConversation,
    ) -> list[AgentMessage]:
        """Prepare in-session messages; compaction can be added here later."""
        del conversation
        return list(messages)

    def to_model_messages(
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
