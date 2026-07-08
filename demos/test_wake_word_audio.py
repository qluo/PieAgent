"""Manual wake word audio demo.

Run this on the Raspberry Pi after installing the project requirements:

    uv run python demos/test_wake_word_audio.py

This is not a unit test. It is a hardware demo for Lesson 3.
It opens the microphone, prints wake word scores, and stops when a score
passes the threshold.
"""

from __future__ import annotations

import argparse
from queue import Queue


SAMPLE_RATE = 16000
CHUNK_SIZE = 1280


def parse_args() -> argparse.Namespace:
    """Read command-line settings.

    Inputs:
    - None directly. Reads settings from the terminal command.

    Output:
    - argparse.Namespace with threshold, model, and device settings.
    """
    parser = argparse.ArgumentParser(description="Test real wake word audio.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Wake score needed to count as detected. Try 0.3 if it is too hard.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional path to an openWakeWord .tflite model file.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Optional microphone device id or name for sounddevice.",
    )
    return parser.parse_args()


def create_model(model_path: str | None):
    """Create the openWakeWord model.

    Inputs:
    - model_path: optional path to a wake word model file.

    Output:
    - An openwakeword Model object.
    """
    try:
        from openwakeword.model import Model
    except ImportError as error:
        raise SystemExit(
            "Missing openwakeword. Run: uv pip install -r requirements.txt"
        ) from error

    if model_path:
        return Model(wakeword_models=[model_path])

    return Model()


def print_scores(scores: dict[str, float]) -> None:
    """Print wake word scores in a kid-friendly format.

    Inputs:
    - scores: dictionary from model name to wake score.

    Output:
    - None. Prints the score line to the terminal.
    """
    if not scores:
        print("Listening... no scores yet")
        return

    parts = [f"{name}: {score:.2f}" for name, score in scores.items()]
    print("Scores -> " + " | ".join(parts))


def main() -> None:
    """Run the real microphone wake word demo.

    Inputs:
    - None directly. Uses command-line options and microphone audio.

    Output:
    - None. Stops after the wake word is detected or Ctrl+C is pressed.
    """
    args = parse_args()

    try:
        import sounddevice as sd
    except ImportError as error:
        raise SystemExit(
            "Missing sounddevice. Run: uv pip install -r requirements.txt"
        ) from error

    model = create_model(args.model)
    audio_queue: Queue = Queue()

    def audio_callback(indata, _frames, _time, status) -> None:
        """Receive one microphone audio chunk.

        Inputs:
        - indata: microphone samples from sounddevice.
        - _frames: number of samples in the chunk.
        - _time: timing information from sounddevice.
        - status: microphone warning/error status.

        Output:
        - None. Adds one audio chunk to audio_queue.
        """
        if status:
            print(f"Microphone status: {status}")
        audio_queue.put(indata[:, 0].copy())

    print("Wake word audio demo")
    print(f"Sample rate: {SAMPLE_RATE} Hz")
    print(f"Threshold: {args.threshold}")
    print("Say the wake word. Press Ctrl+C to stop.")

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=CHUNK_SIZE,
            device=args.device,
            callback=audio_callback,
        ):
            while True:
                audio_chunk = audio_queue.get()
                scores = model.predict(audio_chunk)
                print_scores(scores)

                if scores and max(scores.values()) >= args.threshold:
                    print("Wake word detected!")
                    return
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as error:
        raise SystemExit(
            "Could not read microphone audio. Check the microphone, device "
            f"settings, and permissions. Original error: {error}"
        ) from error


if __name__ == "__main__":
    main()
