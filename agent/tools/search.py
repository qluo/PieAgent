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
        # This limits how many web results DDGS is asked to fetch.
        self.max_results = max_results
        # This tells DDGS which regional version of search to use.
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
        # Implementation guide:
        # 1. Use DDGS as a context manager so it closes its search resources.
        # 2. Call text() with query, self.region, and self.max_results, then
        #    turn the returned iterable into a list.
        # 3. Return a clear message when search fails or returns no results.
        # 4. For the first result, read title, body, and href safely, then make
        #    a labeled Title, Summary, and URL string for the LLM.
        #
        # Expected return value:
        # A short string like:
        #   "Title: ...\nSummary: ...\nURL: ..."

        return ""
