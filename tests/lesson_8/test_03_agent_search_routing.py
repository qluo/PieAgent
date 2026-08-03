from agent.agent import Agent


class RecordingLlm:
    def __init__(self):
        self.search_question = None

    def needs_search(self, question):
        self.search_question = question
        return False

    def answer(self, prompt):
        return prompt


def test_search_decision_uses_the_user_question_not_agent_instructions():
    agent = Agent(
        face_state=None,
        wake_word=None,
        stt=None,
        tts=None,
        llm=RecordingLlm(),
        tools={"search": object()},
    )
    agent.agents_md = "Always be helpful."

    agent.respond("What is the weather today?")

    assert agent.llm.search_question == "What is the weather today?"
