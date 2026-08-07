"""A generic live-web-search agent tool."""

from ddgs import DDGS

from .tools import AgentTool, AgentToolResult


class SearchTool(AgentTool):
    """Search DuckDuckGo and return compact source context to the model."""

    def __init__(self, max_results: int = 1, region: str = "us-en") -> None:
        super().__init__(
            name="web_search",
            description="Search the live web for current information.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The current-information question to search for.",
                    }
                },
                "required": ["query"],
            },
        )
        self.max_results = max_results
        self.region = region

    def execute(self, arguments: dict[str, object]) -> AgentToolResult:
        query = str(arguments.get("query", "")).strip()
        if not query:
            return AgentToolResult("Search requires a query.", "error")
        try:
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(query, region=self.region, max_results=self.max_results)
                )
        except Exception:
            return AgentToolResult(
                "Live search is unavailable. Answer from local knowledge.",
                "error",
                "Live search was unavailable, so I answered from my local knowledge.",
            )

        if not results:
            return AgentToolResult(f"No live search results found for {query}.")
        result = results[0]
        return AgentToolResult(
            "\n".join(
                [
                    f"Title: {result.get('title', '')}",
                    f"Summary: {result.get('body', '')}",
                    f"URL: {result.get('href', '')}",
                ]
            )
        )
