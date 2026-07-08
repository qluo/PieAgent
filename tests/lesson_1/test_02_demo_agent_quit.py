from unittest.mock import patch

from demos import lesson1_demo


def test_demo_agent_can_quit():
    face_state = lesson1_demo.FaceState()
    agent = lesson1_demo.Agent(
        face_state=face_state,
        wake_word=lesson1_demo.FakeWakeWordTool(),
        stt=lesson1_demo.FakeSpeechToTextTool(),
        llm=lesson1_demo.FakeLlmTool(),
        tts=lesson1_demo.FakeTextToSpeechTool(),
    )

    with patch("builtins.input", side_effect=["", "quit"]):
        agent.run()

    assert face_state.get() == "idle"
