from agent.agent import Agent
from agent.tools.llm import LlmUnavailableError
from agent.tools.search import SearchUnavailableError
from face import states


class FakeFaceState:
    def __init__(self):
        self.states = []

    def set(self, state):
        self.states.append(state)


class WakeThenStop:
    def wait(self):
        return None


class EmptyStt:
    def listen_and_transcribe(self):
        return "   "


class RecordingTts:
    def __init__(self):
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)
        raise KeyboardInterrupt


class UnavailableLlm:
    def answer(self, _prompt):
        raise LlmUnavailableError()


class SearchLlm:
    def needs_search(self, _question):
        return True

    def answer(self, prompt):
        return f"local answer to {prompt}"


class FailedSearch:
    def search(self, _question):
        raise SearchUnavailableError()


def test_agent_retries_after_an_empty_transcription():
    face_state = FakeFaceState()
    tts = RecordingTts()
    agent = Agent(
        face_state=face_state,
        wake_word=WakeThenStop(),
        stt=EmptyStt(),
        tts=tts,
        llm=object(),
        tools={},
    )

    try:
        agent.run()
    except KeyboardInterrupt:
        pass

    assert tts.spoken == ["I didn't catch that. Please try again."]
    assert face_state.states == [states.IDLE, states.LISTENING, states.SPEAKING]


def test_agent_returns_a_clear_message_when_ollama_is_unavailable():
    agent = Agent(
        face_state=None,
        wake_word=None,
        stt=None,
        tts=None,
        llm=UnavailableLlm(),
        tools={},
    )
    agent.agents_md = ""

    assert agent.respond("hello") == "I can't reach my language model right now."


def test_agent_falls_back_to_local_knowledge_when_search_fails():
    agent = Agent(
        face_state=None,
        wake_word=None,
        stt=None,
        tts=None,
        llm=SearchLlm(),
        tools={"search": FailedSearch()},
    )
    agent.agents_md = ""

    assert agent.respond("What is the weather?") == (
        "local answer to What is the weather?\n\n"
        "Live search was unavailable, so I answered from my local knowledge."
    )
