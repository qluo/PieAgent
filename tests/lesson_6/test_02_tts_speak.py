import subprocess

from agent.tools.tts import TextToSpeechTool


class FakeInput:
    def __init__(self):
        self.writes = []
        self.closed = False

    def write(self, value):
        self.writes.append(value)

    def close(self):
        self.closed = True


class FakeProcess:
    def __init__(self):
        self.stdin = FakeInput()
        self.stdout = object()
        self.wait_calls = 0

    def wait(self):
        self.wait_calls += 1


def test_tts_streams_piper_audio_to_aplay(monkeypatch):
    piper = FakeProcess()
    player = FakeProcess()
    calls = []

    def fake_popen(command, **kwargs):
        calls.append((command, kwargs))
        return piper if len(calls) == 1 else player

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    tool = TextToSpeechTool(
        voice_model_path="voice.onnx",
        piper_binary="piper",
        player_binary="aplay",
    )

    assert tool.speak("Hello from Pi Agent") is None

    assert len(calls) == 2
    assert calls[0][0][:4] == ["piper", "--model", "voice.onnx", "--output-raw"]
    assert calls[1][0][0] == "aplay"
    assert calls[1][1]["stdin"] is piper.stdout
