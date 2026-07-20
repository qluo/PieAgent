"""Speech-to-text checkpoint for Lesson 5.

Keyboard mode works before microphone transcription is implemented. Switch to
microphone mode after configuring sounddevice and whisper.cpp:

    uv run python -m demos.lesson5_stt_demo
    uv run python -m demos.lesson5_stt_demo --mode microphone
"""

from __future__ import annotations

import argparse

from agent.tools.stt import SpeechToTextTool


def parse_args() -> argparse.Namespace:
    """Read the input mode and transcription settings."""
    parser = argparse.ArgumentParser(description="Try Pie Agent speech-to-text.")
    parser.add_argument(
        "--mode",
        choices=("keyboard", "microphone"),
        default="keyboard",
        help="Use keyboard first, then microphone after Lesson 5 is implemented.",
    )
    parser.add_argument("--seconds", type=float, default=10.0)
    return parser.parse_args()


def main() -> None:
    """Capture one utterance and print its transcription."""
    args = parse_args()
    stt = SpeechToTextTool(mode=args.mode, seconds=args.seconds)
    print(f"STT demo using {args.mode} mode. Press Ctrl+C to stop.")

    try:
        while True:
            text = stt.listen_and_transcribe()
            print(f"Heard: {text}")
            if text.strip().lower() in {"quit", "exit", "stop"}:
                break
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
