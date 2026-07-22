import logging

from ddgs import DDGS


logger = logging.getLogger(__name__)


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
        # Lesson 8: Tools - Web Search
        #
        # Goal:
        # Search the web and return a short piece of text that the LLM can use.
        #
        # Suggested package:
        # - ddgs: provides the DDGS helper.
        #
        # Import after installing requirements:
        #   from ddgs import DDGS
        #
        # Concept to learn:
        # Search tools usually return lots of data. Your job is to shape that
        # data into a small, useful context string.
        #
        # Small first step:
        # Ask for one result with max_results=1.
        #
        # Real version idea:
        # 1. Open DDGS with: with DDGS() as ddgs:
        # 2. Call ddgs.text(query, region="us-en", max_results=1).
        # 3. Pull out the title, href, and body/snippet.
        # 4. Return a short string for the LLM.
        #
        # Expected return value:
        # A short string like:
        #   "Title: ...\nSummary: ...\nURL: ..."

        logger.info("Search: requesting up to %d result(s)", self.max_results)
        try:
            with DDGS() as engine:
                results = list(
                    engine.text(
                        query,
                        region=self.region,
                        max_results=self.max_results,
                    )
                )
        except Exception as error:
            logger.warning("Search: request failed")
            return f"Search failed for {query}: {error}"

        if not results:
            logger.info("Search: no results found")
            return f"No search results found for {query}."

        logger.info("Search: result received")
        result = results[0]
        title = result.get("title", "")
        summary = result.get("body", "")
        url = result.get("href", "")

        return f"Title: {title}\nSummary: {summary}\nURL: {url}"
