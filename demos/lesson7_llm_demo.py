"""Local Ollama checkpoint for Lesson 7.

Start Ollama and pull the teaching model first:

    ollama pull gemma3:1b
    uv run python -m demos.lesson7_llm_demo
"""

from __future__ import annotations

import argparse
from threading import Thread
from time import sleep

from agent.tools.llm import LlmTool


def parse_args() -> argparse.Namespace:
    """Read the local model name and question."""
    parser = argparse.ArgumentParser(description="Ask Pi Agent's local Ollama model.")
    parser.add_argument("question", nargs="?", default="What is a Raspberry Pi?")
    parser.add_argument("--model", default="gemma3:1b")
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser.parse_args()


def main() -> None:
    """Ask one question and print the local model's response."""
    args = parse_args()
    llm = LlmTool(
        model_name=args.model,
        base_url=args.base_url,
        timeout=args.timeout,
    )
    print(f"Model: {args.model}")
    print(f"You: {args.question}")
    result: dict[str, str] = {}

    def get_answer() -> None:
        result["answer"] = llm.answer(args.question)

    worker = Thread(target=get_answer)
    worker.start()
    width = 20
    progress = 0
    while worker.is_alive():
        filled = progress % (width + 1)
        print(f"\rThinking: [{'#' * filled}{'.' * (width - filled)}]", end="", flush=True)
        progress += 1
        sleep(0.2)
    worker.join()
    print("\rThinking: [####################]")
    print(f"Agent: {result['answer']}")


if __name__ == "__main__":
    main()
