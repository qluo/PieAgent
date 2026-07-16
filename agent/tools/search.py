from ddgs import DDGS


class SearchTool:
    """Web search tool using DuckDuckGo search.

    This follows the original Raspberry Pi agent repo's simple approach:
    use the `ddgs` package and its `DDGS` helper.

    Setup idea:
    - Install project packages: uv pip install -r requirements.txt
    - Import DDGS: from ddgs import DDGS
    """

    def __init__(self, max_results: int = 1, region: str = "us-en") -> None:
        """Create the search tool.

        Inputs:
        - max_results: number of search results to ask for.
        - region: DuckDuckGo search region, such as "us-en".

        Output:
        - None. Stores settings for search().
        """
        self.max_results = max_results
        self.region = region

    def search(self, query: str) -> str:
        """Search for information and return text context.

        Inputs:
        - query: the words to search for.

        Output:
        - A short text summary that can be passed into the LLM as context.
        """
        try:
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(
                        query,
                        region=self.region,
                        max_results=self.max_results,
                    )
                )
        except Exception as error:
            return f"Search failed for {query}: {error}"

        if not results:
            return f"No search results found for {query}."

        result = results[0]
        title = result.get("title", "")
        summary = result.get("body", "")
        url = result.get("href", "")

        return f"Title: {title}\nSummary: {summary}\nURL: {url}"
