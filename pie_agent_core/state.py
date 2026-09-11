"""Mutable working state owned by a generic agent."""

from dataclasses import dataclass, field

from .messages import AgentMessage


@dataclass(slots=True)
class AgentState:
    """The in-memory message history for one agent session.

    Applications may supply a subclass when they need additional ephemeral
    state. Durable storage remains an application concern.
    """

    messages: list[AgentMessage] = field(default_factory=list)
