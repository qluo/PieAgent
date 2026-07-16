from agent.agent import Agent


class FakeLlm:
    def __init__(self):
        self.prompts = []

    def answer(self, user_text):
        self.prompts.append(user_text)
        return f"answer to {user_text}"


def test_agent_respond_returns_llm_answer():
    llm = FakeLlm()
    agent = Agent(
        face_state=None,
        wake_word=None,
        stt=None,
        tts=None,
        llm=llm,
        tools={},
    )

    assert agent.respond("hello").endswith("hello")
    assert "hello" in llm.prompts[0]
