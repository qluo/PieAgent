import main


class FakeThread:
    def __init__(self, target, daemon):
        self.target = target
        self.daemon = daemon

    def start(self):
        pass


class FakeAgent:
    created_with = None

    def __init__(self, **kwargs):
        self.__class__.created_with = kwargs

    def run(self):
        pass


class FakeFaceController:
    def __init__(self, face_state):
        self.face_state = face_state

    def run(self):
        pass


def test_main_allows_tts_voice_and_sample_rate_to_be_configured(monkeypatch):
    monkeypatch.setenv("PIE_AGENT_TTS_VOICE_MODEL", "models/piper/custom.onnx")
    monkeypatch.setenv("PIE_AGENT_TTS_SAMPLE_RATE", "16000")
    monkeypatch.setattr(main, "Thread", FakeThread)
    monkeypatch.setattr(main, "Agent", FakeAgent)
    monkeypatch.setattr(main, "FaceController", FakeFaceController)
    monkeypatch.setattr(main, "WakeWordTool", lambda: object())
    monkeypatch.setattr(main, "SpeechToTextTool", lambda: object())
    monkeypatch.setattr(main, "TextToSpeechTool", lambda **kwargs: kwargs)
    monkeypatch.setattr(main, "LlmTool", lambda: object())
    monkeypatch.setattr(main, "SearchTool", lambda: object())

    main.main()

    assert FakeAgent.created_with["tts"] == {
        "voice_model_path": "models/piper/custom.onnx",
        "sample_rate": 16000,
    }
