from agent.agent import Agent
from face.state import FaceState


class OneShotWakeWord:
    def wait(self):
        return None


class OneShotStt:
    def listen_and_transcribe(self):
        return "hello"


class RecordingTts:
    def __init__(self):
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)


class SimpleLlm:
    def answer(self, user_text):
        return f"Hello, you said {user_text}"

    def answer_with_context(self, user_text, context):
        return f"{user_text}: {context}"


def test_agent_parts_can_be_wired_together():
    face_state = FaceState()
    tts = RecordingTts()
    agent = Agent(face_state, OneShotWakeWord(), OneShotStt(), tts, SimpleLlm(), {})

    assert agent.face_state is face_state
    assert agent.tts is tts
    assert agent.respond("hello").startswith("Hello")
