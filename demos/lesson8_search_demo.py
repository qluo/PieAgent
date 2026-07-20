"""Search-routing checkpoint for Lesson 8.

Run after implementing SearchTool and Agent.respond():

    uv run python -m demos.lesson8_search_demo "What happened in space today?"
"""

from __future__ import annotations

import argparse

from agent.agent import Agent
from agent.tools.llm import LlmTool
from agent.tools.search import SearchTool


def parse_args() -> argparse.Namespace:
    """Read the question, model name, and search result limit."""
    parser = argparse.ArgumentParser(description="Ask Pie Agent a question with search routing.")
    parser.add_argument("question", nargs="?", default="What is the latest Raspberry Pi model?")
    parser.add_argument("--model", default="gemma3:1b")
    parser.add_argument("--max-results", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    """Show whether the local LLM uses web-search context for one question."""
    args = parse_args()
    llm = LlmTool(model_name=args.model)
    search = SearchTool(max_results=args.max_results)
    agent = Agent(
        face_state=None,
        wake_word=None,
        stt=None,
        tts=None,
        llm=llm,
        tools={"search": search},
    )

    print(f"You: {args.question}")
    print("Letting the agent decide whether search is needed...")
    print(f"Agent: {agent.respond(args.question)}")


if __name__ == "__main__":
    main()
