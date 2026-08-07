"""Messages kept in an agent conversation."""

from dataclasses import dataclass, field
from typing import Literal

from pie_ai import ToolCall


AgentMessageKind = Literal["user", "assistant", "tool_result", "agent_note"]


@dataclass(slots=True)
class AgentMessage:
    """An entry in the agent's working conversation."""

    kind: AgentMessageKind
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_name: str | None = None


class AgentNote(AgentMessage):
    """Temporary application context that may be made model-visible."""

    def __init__(self, content: str) -> None:
        super().__init__(kind="agent_note", content=content)
