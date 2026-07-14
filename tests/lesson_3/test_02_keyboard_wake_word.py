from agent.tools.wake_word import WakeWordTool


def test_keyboard_wake_word_returns_after_wake(monkeypatch):
    tool = WakeWordTool(mode="keyboard")
    answers = iter(["hello", "wake"])
    typed_words = []

    def fake_input(_prompt=""):
        word = next(answers)
        typed_words.append(word)
        return word

    monkeypatch.setattr("builtins.input", fake_input)

    assert tool.wait() is None
    assert typed_words == ["hello", "wake"]
