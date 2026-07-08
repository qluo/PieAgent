class SearchTool:
    """Web search tool using DuckDuckGo search.

    This follows the original Raspberry Pi agent repo's simple approach:
    use the `duckduckgo_search` package and its `DDGS` helper.

    Setup idea:
    - Install project packages: uv pip install -r requirements.txt
    - Import DDGS: from duckduckgo_search import DDGS
    """

    def search(self, query: str) -> str:
        """Search for information and return text context."""
        # TODO: Import DDGS after installing duckduckgo-search:
        # from duckduckgo_search import DDGS
        #
        # TODO: Use DDGS to search for information related to the query.
        # TODO: Return a short text summary that the LLM can use.
        #
        # Example shape for later:
        # with DDGS() as ddgs:
        #     results = list(ddgs.text(query, region="us-en", max_results=1))
        #     ...
        return ""
