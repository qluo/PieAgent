"""Backward-compatible name for the original conversation state."""

from .state import AgentState


class AgentConversation(AgentState):
    """Compatibility alias for callers that use the original class name."""

    __slots__ = ()
