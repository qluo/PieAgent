from agent.agent import Agent


def test_build_prompt_combines_instructions_and_user_request():
    agent = Agent(None, None, None, None, None, {})
    agent.agents_md = "Be concise."

    prompt = agent.build_prompt("What is Pi Agent?")

    assert "Be concise." in prompt
    assert "What is Pi Agent?" in prompt


def test_build_prompt_keeps_user_request_when_instructions_are_empty():
    agent = Agent(None, None, None, None, None, {})
    agent.agents_md = ""

    assert agent.build_prompt("Hello") == "Hello"
