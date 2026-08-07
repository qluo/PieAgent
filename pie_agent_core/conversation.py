"""The active conversation record for an agent."""

from dataclasses import dataclass, field

from .messages import AgentMessage


@dataclass(slots=True)
class AgentConversation:
    """Working conversation state, without presentation or lifecycle phase."""

    messages: list[AgentMessage] = field(default_factory=list)
