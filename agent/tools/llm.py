import os

import requests


class LlmTool:
    """Ollama LLM tool that can use a local or remote Ollama server.

    Teaching goal:
    - Run the model on the Raspberry Pi instead of using a cloud API.
    - Start with a small open model so students can see the full loop work.

    Setup idea:
    - Install Ollama on the Raspberry Pi.
    - Pull a small model, for example: ollama pull gemma3:1b
    - Ollama usually runs locally at: http://localhost:11434.
    """

    def __init__(
        self,
        model_name: str = "gemma3:1b",
        base_url: str = "http://localhost:11434",
        timeout: float = 60.0,
    ) -> None:
        """Store local or remote Ollama settings.

        Args:
            model_name: Ollama model name to use.
            base_url: Server URL, overridden by ``PI_AGENT_OLLAMA_URL`` when set.
            timeout: Maximum seconds to wait for a response.

        The URL is normalized so ``answer`` can safely append ``/api/generate``.
        """
        self.model_name = model_name
        self.base_url = (
            os.environ.get("PI_AGENT_OLLAMA_URL")
            or base_url
        ).rstrip("/")
        self.timeout = timeout

    def answer(self, user_text: str) -> str:
        """Answer directly using the configured Ollama model.

        Inputs:
        - user_text: the user's question or command.

        Output:
        - The model's answer as a string.
        """
        # Lesson 7: Local LLM
        #
        # Goal:
        # Send the user's text to a local Ollama model and return its answer.
        #
        # Suggested package:
        # - requests: makes HTTP calls to Ollama's local API.
        #
        # Concept to learn:
        # Ollama runs a local web server at self.base_url. Your Python code
        # sends a prompt to that server and receives generated text back.
        #
        # Implementation guide:
        # 1. Build the endpoint by adding /api/generate to self.base_url.
        # 2. POST JSON containing self.model_name, user_text as the prompt,
        #    and stream=False so one complete response is returned.
        # 3. Use self.timeout and raise an error for unsuccessful HTTP results.
        # 4. Read the response JSON and strip whitespace from its response text.
        #
        # Expected return value:
        # A string response from the local model.

        return ""

    def needs_search(self, user_text: str) -> bool:
        """Ask the local model whether a web search would help."""
        # Lesson 8 helper:
        # 1. Build a short prompt that includes user_text.
        # 2. Ask the LLM to answer with exactly SEARCH or NO_SEARCH.
        # 3. Normalize the returned text by removing whitespace and using
        #    uppercase letters before deciding.
        # 4. Return True for SEARCH and False for NO_SEARCH.
        return False

    def answer_with_context(self, user_text: str, context: str) -> str:
        """Answer using tool context and a local Ollama model.

        Inputs:
        - user_text: the user's question or command.
        - context: extra information from a tool, such as search results.

        Output:
        - The model's answer as a string, using the context when helpful.
        """
        # Lesson 8: Search + LLM
        #
        # Goal:
        # Give the local LLM extra information from a tool, such as web
        # search results, before it answers.
        #
        # Concept to learn:
        # The LLM does not automatically know what your search tool found.
        # You must include the search result inside the prompt.
        #
        # Implementation guide:
        # 1. Build one prompt with clearly labeled context and question sections.
        # 2. Call self.answer(prompt) so this method reuses the Ollama request
        #    code instead of making a second HTTP implementation.
        # 3. Return that answer unchanged.
        #
        # Expected return value:
        # A string response that uses the tool context.
        return ""
