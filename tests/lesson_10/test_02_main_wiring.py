import main


class FakeThread:
    started = []

    def __init__(self, target, daemon):
        self.target = target
        self.daemon = daemon

    def start(self):
        self.started.append((self.target, self.daemon))


class FakeAgent:
    created_with = None
    ran = False

    def __init__(self, **kwargs):
        self.__class__.created_with = kwargs

    def run(self):
        self.__class__.ran = True


class FakeFaceController:
    def __init__(self, face_state):
        self.face_state = face_state

    def run(self):
        return None


def test_main_starts_the_face_thread_and_wires_the_agent(monkeypatch):
    FakeThread.started = []
    FakeAgent.created_with = None
    FakeAgent.ran = False
    monkeypatch.setattr(main, "Thread", FakeThread)
    monkeypatch.setattr(main, "Agent", FakeAgent)
    monkeypatch.setattr(main, "FaceController", FakeFaceController)
    monkeypatch.setattr(main, "WakeWordTool", lambda: "wake")
    monkeypatch.setattr(main, "SpeechToTextTool", lambda: "stt")
    monkeypatch.setattr(main, "TextToSpeechTool", lambda: "tts")
    monkeypatch.setattr(main, "LlmTool", lambda model_name: ("llm", model_name))
    monkeypatch.setattr(main, "SearchTool", lambda: "search")

    main.main()

    assert len(FakeThread.started) == 1
    assert FakeThread.started[0][1] is True
    assert FakeAgent.created_with["wake_word"] == "wake"
    assert FakeAgent.created_with["stt"] == "stt"
    assert FakeAgent.created_with["tts"] == "tts"
    assert FakeAgent.created_with["llm"] == ("llm", "gemma3:1b")
    assert FakeAgent.created_with["tools"] == {"search": "search"}
    assert FakeAgent.ran is True
