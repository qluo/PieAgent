import os
from threading import Thread

from agent.agent import Agent
from agent.tools.llm import LlmTool
from agent.tools.kokoro_tts import KokoroTextToSpeechTool
from agent.tools.search import SearchTool
from agent.tools.stt import SpeechToTextTool
from agent.tools.tts import TextToSpeechTool
from agent.tools.wake_word import WakeWordTool
from face.controller import FaceController
from face.state import FaceState


def main() -> None:
    """Start the face controller and agent.

    Inputs:
    - None. Creates all objects inside the function.

    Output:
    - None. Runs until the agent program is stopped.
    """
    face_state = FaceState()

    face_controller = FaceController(face_state=face_state)
    Thread(target=face_controller.run, daemon=True).start()

    tts_engine = os.environ.get("PIE_AGENT_TTS_ENGINE", "piper").lower()
    if tts_engine == "kokoro":
        tts = KokoroTextToSpeechTool(
            model_path=os.environ.get(
                "PIE_AGENT_TTS_KOKORO_MODEL",
                "models/kokoro/kokoro-v1.0.int8.onnx",
            ),
            voices_path=os.environ.get(
                "PIE_AGENT_TTS_KOKORO_VOICES",
                "models/kokoro/voices-v1.0.bin",
            ),
            voice=os.environ.get("PIE_AGENT_TTS_KOKORO_VOICE", "af_sarah"),
            speed=float(os.environ.get("PIE_AGENT_TTS_KOKORO_SPEED", "1.0")),
        )
    elif tts_engine == "piper":
        tts = TextToSpeechTool(
            voice_model_path=os.environ.get(
                "PIE_AGENT_TTS_VOICE_MODEL",
                "models/piper/en_US-lessac-medium.onnx",
            ),
            sample_rate=int(os.environ.get("PIE_AGENT_TTS_SAMPLE_RATE", "22050")),
        )
    else:
        raise ValueError('PIE_AGENT_TTS_ENGINE must be "piper" or "kokoro".')

    wake_word_mode = os.environ.get("PIE_AGENT_WAKE_WORD_MODE", "microphone")
    wake_word = (
        WakeWordTool()
        if wake_word_mode == "microphone"
        else WakeWordTool(mode=wake_word_mode)
    )
    stt_mode = os.environ.get("PIE_AGENT_STT_MODE", "microphone")
    stt = (
        SpeechToTextTool()
        if stt_mode == "microphone"
        else SpeechToTextTool(mode=stt_mode)
    )

    agent = Agent(
        face_state=face_state,
        wake_word=wake_word,
        stt=stt,
        tts=tts,
        llm=LlmTool(),
        tools={
            "search": SearchTool(),
        },
    )
    agent.run()


if __name__ == "__main__":
    main()
