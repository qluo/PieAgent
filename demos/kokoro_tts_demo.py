"""Speak one sentence with the local Kokoro voice.

Run after downloading the model files described in docs/setup.md:
    PIE_AGENT_TTS_ENGINE=kokoro uv run python demos/kokoro_tts_demo.py
"""

import os

from pie_voice_agent.kokoro_tts import KokoroTextToSpeechTool


def main() -> None:
    tool = KokoroTextToSpeechTool(
        voice=os.environ.get("PIE_AGENT_TTS_KOKORO_VOICE", "af_sarah"),
        speed=float(os.environ.get("PIE_AGENT_TTS_KOKORO_SPEED", "1.0")),
    )
    tool.speak("Hello. I am Pi Agent, speaking with a local Kokoro voice.")


if __name__ == "__main__":
    main()
