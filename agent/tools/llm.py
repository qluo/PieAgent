class LlmTool:
    """Local LLM tool powered by Ollama.

    Teaching goal:
    - Run the model on the Raspberry Pi instead of using a cloud API.
    - Start with a small open model so students can see the full loop work.

    Setup idea:
    - Install Ollama on the Raspberry Pi.
    - Pull a small model, for example: ollama pull llama3.2:1b
    - Ollama usually runs locally at: http://localhost:11434
    """

    def __init__(self, model_name: str = "llama3.2:1b"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"

    def answer(self, user_text: str) -> str:
        """Answer directly using a local Ollama model."""
        # TODO: Send user_text to Ollama's local chat API.
        # TODO: Return the model's answer as a string.
        return ""

    def answer_with_context(self, user_text: str, context: str) -> str:
        """Answer using tool context and a local Ollama model."""
        # TODO: Combine user_text and context into one prompt.
        # TODO: Send the prompt to Ollama's local chat API.
        # TODO: Return the model's answer as a string.
        return ""
