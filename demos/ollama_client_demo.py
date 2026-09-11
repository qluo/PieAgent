"""Exercise OllamaClient directly, without the agent or voice layers."""

import argparse
import os

from pie_ai import (
    ModelMessage,
    ModelResponse,
    ModelUnavailableError,
    OllamaClient,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="?", default="Reply with OK.")
    parser.add_argument("--stream", action="store_true")
    args = parser.parse_args()

    client = OllamaClient(model_name=os.environ.get("PIE_AGENT_MODEL", "qwen3:1.7b"))
    try:
        generated = client.generate(
            [ModelMessage(role="user", content=args.prompt)],
            streaming=args.stream,
        )
        if isinstance(generated, ModelResponse):
            print(generated.message.content)
            return

        for event in generated:
            if event.kind == "text_delta":
                print(event.text, end="", flush=True)
        print()
    except ModelUnavailableError:
        print("I can't reach my language model right now.")


if __name__ == "__main__":
    main()
