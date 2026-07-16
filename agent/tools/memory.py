from pathlib import Path


DEFAULT_MEMORY_DIR = Path(__file__).resolve().parents[2] / "memory"


class MemoryTool:
    """Store a small amount of local agent memory in Markdown files."""

    conversation_heading = "# Conversation Memory\n\n"
    facts_heading = "# Remembered Facts\n\n"
    turn_marker = "## Turn\n"

    def __init__(
        self, memory_dir: Path | str = DEFAULT_MEMORY_DIR, max_turns: int = 5
    ) -> None:
        """Create Markdown memory files and limit stored conversation turns."""
        self.memory_dir = Path(memory_dir)
        self.max_turns = max_turns
        self.conversation_file = self.memory_dir / "conversation.md"
        self.facts_file = self.memory_dir / "facts.md"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_file(self.conversation_file, self.conversation_heading)
        self._ensure_file(self.facts_file, self.facts_heading)

    def recent_conversation(self) -> str:
        """Return the newest stored conversation turns as Markdown text."""
        return "\n".join(self._turns()[-self.max_turns:]).strip()

    def facts(self) -> list[str]:
        """Return durable user facts without their Markdown bullet markers."""
        return [
            line[2:].strip()
            for line in self.facts_file.read_text(encoding="utf-8").splitlines()
            if line.startswith("- ") and line[2:].strip()
        ]

    def remember(self, fact: str) -> None:
        """Append an explicitly requested fact to durable memory."""
        fact = fact.strip()
        if not fact:
            return
        with self.facts_file.open("a", encoding="utf-8") as file:
            file.write(f"- {fact}\n")

    def record_turn(self, user_text: str, assistant_text: str) -> None:
        """Store a completed exchange, retaining only the newest turns."""
        turn = (
            f"{self.turn_marker}"
            f"**User:**\n{user_text.strip()}\n\n"
            f"**Assistant:**\n{assistant_text.strip()}\n"
        )
        turns = [*self._turns(), turn][-self.max_turns:]
        self.conversation_file.write_text(
            self.conversation_heading + "\n".join(turns), encoding="utf-8"
        )

    def _turns(self) -> list[str]:
        """Read complete turns, excluding the document heading."""
        content = self.conversation_file.read_text(encoding="utf-8")
        return [
            f"{self.turn_marker}{turn.strip()}"
            for turn in content.split(self.turn_marker)[1:]
            if turn.strip()
        ]

    @staticmethod
    def _ensure_file(path: Path, heading: str) -> None:
        if not path.exists():
            path.write_text(heading, encoding="utf-8")
