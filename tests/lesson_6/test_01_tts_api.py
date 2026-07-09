from agent.tools.tts import TextToSpeechTool


def test_tts_tool_has_speak_method():
    tool = TextToSpeechTool(voice_model_path="voice.onnx")

    assert hasattr(tool, "speak")
