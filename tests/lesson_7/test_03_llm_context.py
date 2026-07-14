from agent.tools.llm import LlmTool


def test_answer_with_context_builds_a_prompt_and_uses_answer(monkeypatch):
    tool = LlmTool()
    prompts = []

    def fake_answer(prompt):
        prompts.append(prompt)
        return "contextual answer"

    monkeypatch.setattr(tool, "answer", fake_answer)

    assert tool.answer_with_context("What is PiAgent?", "PiAgent is a teaching project.") == "contextual answer"
    assert "What is PiAgent?" in prompts[0]
    assert "PiAgent is a teaching project." in prompts[0]
