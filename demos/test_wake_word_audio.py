"""Manual wake word audio demo for Lesson 3.

Run this on the Raspberry Pi after implementing WakeWordTool:

    uv run python demos/test_wake_word_audio.py

This is not a unit test. It calls the student's microphone wake word code in
agent/tools/wake_word.py.
"""

from __future__ import annotations

import argparse

from agent.tools.wake_word import DEFAULT_WAKE_WORD_MODEL, WakeWordTool


def parse_args() -> argparse.Namespace:
    """Read the model and threshold chosen in the terminal."""
    parser = argparse.ArgumentParser(description="Test real wake word audio.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Wake score needed to count as detected. Try 0.3 if it is too hard.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_WAKE_WORD_MODEL,
        help="openWakeWord model name or local model path.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the student's microphone wake word implementation."""
    args = parse_args()
    wake_word = WakeWordTool(
        model_path=args.model,
        threshold=args.threshold,
        mode="microphone",
    )

    print("Wake word audio demo")
    print(f"Threshold: {args.threshold}")
    print("Say the wake word. Press Ctrl+C to stop.")

    try:
        wake_word.wait()
    except KeyboardInterrupt:
        print("\nStopped.")
        return

    print("Wake word detected!")


if __name__ == "__main__":
    main()
