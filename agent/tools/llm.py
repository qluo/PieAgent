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
        # Ollama uses this name to choose which downloaded model should answer.
        self.model_name = model_name
        # Remove a final slash so answer() can safely add /api/generate.
        self.base_url = (
            os.environ.get("PI_AGENT_OLLAMA_URL")
            or base_url
        ).rstrip("/")
        # requests.post() uses this to stop waiting after too long.
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
        # 3. Normalize the returned text by removing whitespace and using
        #    uppercase letters before deciding.
        # 4. Return True for SEARCH and False for NO_SEARCH.
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
        # Implementation guide:
        # 1. Build one prompt with clearly labeled context and question sections.
        # 2. Call self.answer(prompt) so this method reuses the Ollama request
        #    code instead of making a second HTTP implementation.
        # 3. Return that answer unchanged.
        #
        # Expected return value:
        # A string response that uses the tool context.
        prompt = (
            "Use this context to answer the user's question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{user_text}"
        )
        return self.answer(prompt)
