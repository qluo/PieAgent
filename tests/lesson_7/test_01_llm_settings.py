from agent.tools.llm import LlmTool


def test_llm_tool_stores_local_ollama_settings():
    tool = LlmTool(
        model_name="test-model",
        base_url="http://example.test:11434",
        timeout=12.5,
    )

    assert tool.model_name == "test-model"
    assert tool.base_url == "http://example.test:11434"
    assert tool.timeout == 12.5
