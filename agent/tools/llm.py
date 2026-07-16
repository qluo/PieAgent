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
        """Create the local LLM tool.

        Inputs:
        - model_name: Ollama model name to use on the selected server.
        - base_url: Ollama server URL. Defaults to ``PI_AGENT_OLLAMA_URL`` or
          the local server at ``http://localhost:11434``.
        - timeout: maximum seconds to wait for an Ollama response.

        Output:
        - None. Stores model settings for later requests.
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
        # Small first step:
        # Test Ollama in the terminal first:
        #   ollama run gemma3:1b
        #
        # Real version idea:
        # 1. Send a POST request to an Ollama endpoint.
        # 2. Include self.model_name and user_text in the request body.
        # 3. Parse the JSON response.
        # 4. Return only the answer text.
        #
        # Expected return value:
        # A string response from the local model.

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model_name, "prompt": user_text, "stream": False},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["response"].strip()

    def needs_search(self, user_text: str) -> bool:
        """Ask the local model whether a web search would help."""
        # Lesson 8 helper:
        # 1. Build a short prompt that includes user_text.
        # 2. Ask the LLM to answer with exactly SEARCH or NO_SEARCH.
        # 3. Return True for SEARCH and False for NO_SEARCH.
        prompt = (
            "Based on your current knowledge, decide if this user question needs current web search results.\n"
            "Answer with only SEARCH or NO_SEARCH.\n\n"
            f"Question: {user_text}"
        )
        decision = self.answer(prompt).strip().upper()
        return decision.startswith("SEARCH")

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
        # Small first step:
        # Build one combined prompt string:
        #   "User question: ... Search result: ..."
        #
        # Real version idea:
        # 1. Combine user_text and context into a clear prompt.
        # 2. Send that prompt to Ollama the same way answer(...) does.
        # 3. Return only the final answer text.
        #
        # Expected return value:
        # A string response that uses the tool context.
        prompt = (
            "Use this context to answer the user's question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{user_text}"
        )
        return self.answer(prompt)
