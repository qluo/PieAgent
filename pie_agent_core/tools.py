"""Executable tools used by the generic agent loop."""

from dataclasses import dataclass
from typing import Literal

from pie_ai import ToolSchema


ToolStatus = Literal["success", "error", "declined"]


@dataclass(slots=True)
class AgentToolResult:
    """A tool result stored in the conversation and returned to the model."""

    content: str
    status: ToolStatus = "success"
    user_notice: str | None = None


class AgentTool(ToolSchema):
    """A declarative tool schema with executable behavior."""

    def execute(self, arguments: dict[str, object]) -> AgentToolResult:
        raise NotImplementedError
