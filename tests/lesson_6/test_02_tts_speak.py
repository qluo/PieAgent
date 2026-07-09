from agent.tools.tts import TextToSpeechTool


class FakePipe:
    def __init__(self):
        self.closed = False

    def write(self, _data):
        pass

    def close(self):
        self.closed = True


class FakeProcess:
    def __init__(self, *args, **kwargs):
        self.stdin = FakePipe()
        self.stdout = FakePipe()

    def wait(self):
        return 0


def test_tts_speak_finishes_without_error(monkeypatch):
    monkeypatch.setattr("subprocess.Popen", FakeProcess)
    tool = TextToSpeechTool(voice_model_path="voice.onnx")

    assert tool.speak("Hello from my Pi agent") is None
