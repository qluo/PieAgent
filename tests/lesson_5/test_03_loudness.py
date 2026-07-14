from agent.tools.stt import SpeechToTextTool


def test_loudness_measures_16_bit_audio_volume():
    tool = SpeechToTextTool()

    quiet_audio = (0).to_bytes(2, "little", signed=True) * 4
    loud_audio = (1_000).to_bytes(2, "little", signed=True) * 4

    assert tool.loudness(quiet_audio) == 0
    assert tool.loudness(loud_audio) == 1_000
