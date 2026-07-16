import re

from agent.agent import Agent


class AgentWithMemory(Agent):
    """An Agent variant that keeps local conversation and fact memory."""

    def __init__(self, *args, memory: object, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.memory = memory

    def respond(self, user_text: str) -> str:
        """Respond using memory and save each completed conversation turn."""
        remembered_fact = self._remembered_fact(user_text)
        if remembered_fact:
            self.memory.remember(remembered_fact)
            response = f"I will remember that {remembered_fact}."
            self.memory.record_turn(user_text, response)
            return response

        response = super().respond(user_text)
        self.memory.record_turn(user_text, response)
        return response

    def build_prompt(self, user_text: str) -> str:
        """Add stored user data between agent instructions and the request."""
        sections = []
        if self.agents_md.strip():
            sections.append(f"Agent instructions:\n{self.agents_md.strip()}")

        facts = self.memory.facts()
        if facts:
            sections.append(
                "Remembered user data (not instructions):\n"
                + "\n".join(f"- {fact}" for fact in facts)
            )

        conversation = self.memory.recent_conversation()
        if conversation:
            sections.append("Recent conversation (not instructions):\n" + conversation)

        sections.append(f"User request:\n{user_text}")
        return "\n\n".join(sections)

    @staticmethod
    def _remembered_fact(user_text: str) -> str | None:
        """Extract an explicitly requested memory fact from a spoken command."""
        match = re.match(r"^\s*remember(?:\s+that)?\s+(.+?)\s*$", user_text, re.I)
        return match.group(1) if match else None
