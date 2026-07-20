from agent.agent import Agent


def test_build_prompt_combines_instructions_and_user_request():
    agent = Agent(None, None, None, None, None, {})
    agent.agents_md = "Be concise."

    prompt = agent.build_prompt("What is Pie Agent?")

    assert prompt == (
        "Agent instructions:\nBe concise.\n\n"
        "User request:\nWhat is Pie Agent?"
    )


def test_build_prompt_keeps_user_request_when_instructions_are_empty():
    agent = Agent(None, None, None, None, None, {})
    agent.agents_md = ""

    assert agent.build_prompt("Hello") == "Hello"


def test_build_prompt_treats_whitespace_only_instructions_as_empty():
    agent = Agent(None, None, None, None, None, {})
    agent.agents_md = " \n\t "

    assert agent.build_prompt("Hello") == "Hello"
