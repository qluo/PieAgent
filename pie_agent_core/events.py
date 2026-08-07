"""Neutral agent lifecycle events."""

from dataclasses import dataclass
from typing import Literal

from .messages import AgentMessage
from .tools import AgentToolResult


AgentEventKind = Literal[
    "agent_started",
    "agent_finished",
    "turn_started",
    "turn_finished",
    "tool_started",
    "tool_finished",
]


@dataclass(slots=True)
class AgentEvent:
    """A lifecycle transition emitted by the core agent."""

    kind: AgentEventKind
    message: AgentMessage | None = None
    tool_name: str | None = None
    result: AgentToolResult | None = None
