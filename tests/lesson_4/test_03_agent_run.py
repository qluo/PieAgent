import pytest

from agent.agent import Agent
from face import states


class RecordingFaceState:
    def __init__(self):
        self.values = []

    def set(self, state):
        self.values.append(state)


class OneTurnWakeWord:
    def __init__(self):
        self.calls = 0

    def wait(self):
        self.calls += 1
        if self.calls > 1:
            raise StopIteration


class FakeStt:
    def listen_and_transcribe(self):
        return "hello"


class FakeTts:
    def __init__(self):
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)


class FakeLlm:
    def answer(self, user_text):
        return f"answer to {user_text}"


def test_agent_run_completes_one_interaction_then_returns_to_idle():
    face_state = RecordingFaceState()
    tts = FakeTts()
    agent = Agent(
        face_state=face_state,
        wake_word=OneTurnWakeWord(),
        stt=FakeStt(),
        tts=tts,
        llm=FakeLlm(),
        tools={},
    )

    with pytest.raises(StopIteration):
        agent.run()

    assert face_state.values[:5] == [
        states.IDLE,
        states.LISTENING,
        states.THINKING,
        states.SPEAKING,
        states.IDLE,
    ]
    assert tts.spoken == ["answer to hello"]
