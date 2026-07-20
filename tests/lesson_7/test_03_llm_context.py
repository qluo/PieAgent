from agent.tools.llm import LlmTool


def test_answer_with_context_builds_a_prompt_and_uses_answer(monkeypatch):
    tool = LlmTool()
    prompts = []

    def fake_answer(prompt):
        prompts.append(prompt)
        return "contextual answer"

    monkeypatch.setattr(tool, "answer", fake_answer)

    assert tool.answer_with_context("What is Pie Agent?", "Pie Agent is a teaching project.") == "contextual answer"
    assert "Context:" in prompts[0]
    assert "Question:" in prompts[0]
    assert "What is Pie Agent?" in prompts[0]
    assert "Pie Agent is a teaching project." in prompts[0]
