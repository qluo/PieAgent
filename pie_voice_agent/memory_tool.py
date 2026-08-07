"""Voice-owned tool that persists an explicitly remembered fact."""

from pie_agent_core import AgentTool, AgentToolResult

from .memory import MarkdownMemory


class RememberFactTool(AgentTool):
    """Store a user fact only when the model requests this explicit tool."""

    def __init__(self, memory: MarkdownMemory) -> None:
        super().__init__(
            name="remember_fact",
            description="Save an explicitly requested user fact for future conversations.",
            parameters={
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "The fact the user explicitly asked the assistant to remember.",
                    }
                },
                "required": ["fact"],
            },
        )
        self.memory = memory

    def execute(self, arguments: dict[str, object]) -> AgentToolResult:
        fact = str(arguments.get("fact", "")).strip()
        if not fact:
            return AgentToolResult("A non-empty fact is required.", "error")
        self.memory.remember(fact)
        return AgentToolResult(f"Saved this fact for future conversations: {fact}")
