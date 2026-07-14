from agent.tools.wake_word import WakeWordTool


def test_wait_uses_the_keyboard_helper_in_keyboard_mode(monkeypatch):
    tool = WakeWordTool(mode="keyboard")
    calls = []

    monkeypatch.setattr(tool, "_wait_for_keyboard_wake", lambda: calls.append("keyboard"))
    monkeypatch.setattr(tool, "_wait_for_microphone_wake", lambda: calls.append("microphone"))

    tool.wait()

    assert calls == ["keyboard"]
