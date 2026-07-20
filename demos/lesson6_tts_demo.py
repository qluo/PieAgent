"""Text-to-speech checkpoint for Lesson 6.

Run after configuring Piper and an audio player:

    uv run python -m demos.lesson6_tts_demo
"""

from __future__ import annotations

import argparse

from agent.tools.tts import TextToSpeechTool


def parse_args() -> argparse.Namespace:
    """Read the sentence and optional local binary paths."""
    parser = argparse.ArgumentParser(description="Make Pie Agent speak one sentence.")
    parser.add_argument("--text", default="Hello! I am Pie Agent.")
    parser.add_argument("--voice-model", default="models/piper/en_US-lessac-low.onnx")
    parser.add_argument("--piper", default="tools/piper/piper")
    parser.add_argument("--player", default="aplay")
    return parser.parse_args()


def main() -> None:
    """Send one sentence to the configured text-to-speech tool."""
    args = parse_args()
    tts = TextToSpeechTool(
        voice_model_path=args.voice_model,
        piper_binary=args.piper,
        player_binary=args.player,
    )
    print(f"Speaking: {args.text}")
    tts.speak(args.text)
    print("Done.")


if __name__ == "__main__":
    main()
