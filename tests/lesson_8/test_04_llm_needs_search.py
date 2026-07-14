from agent.tools.llm import LlmTool


def test_needs_search_uses_the_llm_decision(monkeypatch):
    tool = LlmTool()

    monkeypatch.setattr(tool, "answer", lambda _prompt: "SEARCH")
    assert tool.needs_search("What is the weather today?") is True

    monkeypatch.setattr(tool, "answer", lambda _prompt: "NO_SEARCH")
    assert tool.needs_search("What is two plus two?") is False
