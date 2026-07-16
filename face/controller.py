from face.renderer import FaceRenderer
from face.state import FaceState
import time


class FaceController:
    def __init__(self, face_state: FaceState, renderer: FaceRenderer | None = None) -> None:
        """Create the face controller.

        Inputs:
        - face_state: shared FaceState object to read the current face state.
        - renderer: optional FaceRenderer. If None, students can create one
          inside their implementation.

        Output:
        - None. The controller stores the inputs for later use.
        """
        self.face_state = face_state
        self.renderer = renderer

    def run_once(self) -> None:
        """Render one face frame.

        Inputs:
        - None directly. Reads self.face_state and uses self.renderer.

        Output:
        - None. Draws exactly one frame as a side effect.
        """
        if self.renderer is None:
            self.renderer = FaceRenderer()

        state = self.face_state.get()
        self.renderer.draw(state)

    def run(self, sleep_seconds: float = 0.1) -> None:
        """Continuously render the face matching the latest FaceState.

        Inputs:
        - sleep_seconds: pause between frames. Reads self.face_state and uses
          self.renderer.

        Output:
        - None. This method keeps running until the program is stopped.
        """
        if self.renderer is None:
            self.renderer = FaceRenderer()

        self.renderer.load()
        while True:
            self.run_once()
            time.sleep(sleep_seconds)
