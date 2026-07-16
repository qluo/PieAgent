"""Face-state animation checkpoint for Lesson 2.

Run after completing the face renderer and controller:

    uv run python -m demos.lesson2_face_demo
"""

from __future__ import annotations

import argparse
from threading import Thread
from time import sleep

from face import states
from face.controller import FaceController
from face.renderer import FaceRenderer
from face.state import FaceState


DEMO_STATES = (states.IDLE, states.LISTENING, states.THINKING, states.SPEAKING)


def parse_args() -> argparse.Namespace:
    """Read how long each expression should remain visible."""
    parser = argparse.ArgumentParser(description="Cycle through Pi Agent face states.")
    parser.add_argument(
        "--seconds-per-state",
        type=float,
        default=2.0,
        help="Seconds to show each face before changing it (default: 2).",
    )
    return parser.parse_args()


def main() -> None:
    """Start the renderer and show each main face state in sequence."""
    args = parse_args()
    face_state = FaceState()
    controller = FaceController(face_state, renderer=FaceRenderer())
    Thread(target=controller.run, daemon=True).start()

    print("Face demo running.")
    try:
        for number, state in enumerate(DEMO_STATES, start=1):
            print(f"Showing {number}/{len(DEMO_STATES)}: {state}")
            face_state.set(state)
            sleep(args.seconds_per_state)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        face_state.set(states.IDLE)
        print("Face demo complete.")


if __name__ == "__main__":
    main()
