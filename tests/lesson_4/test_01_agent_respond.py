from agent.agent import Agent


class FakeLlm:
    def answer(self, user_text):
        return f"answer to {user_text}"


def test_agent_respond_returns_llm_answer():
    agent = Agent(
        face_state=None,
        wake_word=None,
        stt=None,
        tts=None,
        llm=FakeLlm(),
        tools={},
    )

    assert agent.respond("hello") == "answer to hello"


def test_agent_respond_includes_agents_md_in_llm_prompt():
    agent = Agent(
        face_state=None,
        wake_word=None,
        stt=None,
        tts=None,
        llm=FakeLlm(),
        tools={},
    )
    agent.agents_md = "Answer in one sentence."

    assert agent.respond("hello") == (
        "answer to Project instructions:\n"
        "Answer in one sentence.\n\n"
        "User request:\n"
        "hello"
    )
