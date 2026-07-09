import requests


class LlmTool:
    """Local LLM tool powered by Ollama.

    Teaching goal:
    - Run the model on the Raspberry Pi instead of using a cloud API.
    - Start with a small open model so students can see the full loop work.

    Setup idea:
    - Install Ollama on the Raspberry Pi.
    - Pull a small model, for example: ollama pull gemma3:1b
    - Ollama usually runs locally at: http://localhost:11434
    """

    def __init__(self, model_name: str = "gemma3:1b") -> None:
        """Create the local LLM tool.

        Inputs:
        - model_name: Ollama model name to use.

        Output:
        - None. Stores model settings for later requests.
        """
        self.model_name = model_name
        self.base_url = "http://localhost:11434"

    def answer(self, user_text: str) -> str:
        """Answer directly using a local Ollama model.

        Inputs:
        - user_text: the user's question or command.

        Output:
        - The model's answer as a string.
        """
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": user_text,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["response"].strip()

    def needs_search(self, user_text: str) -> bool:
        """Ask the local model if this question needs a web search."""
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
        prompt = (
            "Use this context to answer the user's question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{user_text}"
        )
        return self.answer(prompt)
