"""Compose the local voice application from the three Pie Agent layers."""

import os
from pathlib import Path
from threading import Thread

from pie_ai import OllamaClient
from pie_agent_core import Agent, Context
from pie_agent_core.search import SearchTool
from pie_voice_agent import VoiceAgent
from pie_voice_agent.face.controller import FaceController
from pie_voice_agent.face.state import FaceState
from pie_voice_agent.kokoro_tts import KokoroTextToSpeechTool
from pie_voice_agent.memory import MarkdownMemory
from pie_voice_agent.memory_tool import RememberFactTool
from pie_voice_agent.stt import SpeechToTextTool
from pie_voice_agent.tts import TextToSpeechTool
from pie_voice_agent.wake_word import WakeWordTool


PROJECT_ROOT = Path(__file__).resolve().parent


def load_system_prompt() -> str:
    """Read the voice application's optional project instructions."""
    instructions = PROJECT_ROOT / "AGENTS.md"
    return instructions.read_text(encoding="utf-8") if instructions.is_file() else ""


def build_tts() -> object:
    """Create the selected local text-to-speech adapter."""
    tts_engine = os.environ.get("PIE_AGENT_TTS_ENGINE", "piper").lower()
    if tts_engine == "kokoro":
        return KokoroTextToSpeechTool(
            model_path=os.environ.get(
                "PIE_AGENT_TTS_KOKORO_MODEL",
                "models/kokoro/kokoro-v0_19.onnx",
            ),
            voices_path=os.environ.get(
                "PIE_AGENT_TTS_KOKORO_VOICES",
                "models/kokoro/voices.json",
            ),
            voice=os.environ.get("PIE_AGENT_TTS_KOKORO_VOICE", "af_sarah"),
            speed=float(os.environ.get("PIE_AGENT_TTS_KOKORO_SPEED", "1.0")),
        )
    if tts_engine == "piper":
        return TextToSpeechTool(
            voice_model_path=os.environ.get(
                "PIE_AGENT_TTS_VOICE_MODEL",
                "models/piper/en_US-lessac-medium.onnx",
            ),
            sample_rate=int(os.environ.get("PIE_AGENT_TTS_SAMPLE_RATE", "22050")),
        )
    raise ValueError('PIE_AGENT_TTS_ENGINE must be "piper" or "kokoro".')


def main() -> None:
    """Start the complete local voice agent."""
    face_state = FaceState()
    face_controller = FaceController(face_state=face_state)
    face_thread = Thread(target=face_controller.run, daemon=True)
    face_thread.start()

    memory = MarkdownMemory()
    core_agent = Agent(
        model_client=OllamaClient(
            model_name=os.environ.get("PIE_AGENT_MODEL", "qwen3:1.7b")
        ),
        tools=[SearchTool(), RememberFactTool(memory)],
        context=Context(system_prompt=load_system_prompt()),
        thinking_mode=os.environ.get("PIE_AGENT_THINKING", "auto").lower(),
    )

    wake_word_mode = os.environ.get("PIE_AGENT_WAKE_WORD_MODE", "microphone")
    stt_mode = os.environ.get("PIE_AGENT_STT_MODE", "microphone")
    voice_agent = VoiceAgent(
        agent=core_agent,
        face_state=face_state,
        wake_word=WakeWordTool(mode=wake_word_mode),
        stt=SpeechToTextTool(
            mode=stt_mode,
            model_path=os.environ.get(
                "PIE_AGENT_STT_MODEL", "models/ggml-small.en.bin"
            ),
        ),
        tts=build_tts(),
        memory=memory,
        streaming=os.environ.get("PIE_AGENT_STREAMING", "").lower()
        in {"1", "true", "yes"},
    )
    try:
        voice_agent.run()
    finally:
        face_controller.stop()
        face_thread.join(timeout=1)


if __name__ == "__main__":
    main()
