from face.renderer import FaceRenderer
from face.state import FaceState
import time


class FaceController:
    def __init__(self, face_state: FaceState, renderer: FaceRenderer | None = None) -> None:
        """Create the controller that connects shared state to the renderer.

        Args:
            face_state: Shared state written by the agent and read for drawing.
            renderer: Optional renderer. Tests supply a fake; otherwise the
                controller creates a ``FaceRenderer`` when it first runs.
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
        # Lesson 2: Testable Face Controller Step
        #
        # Goal:
        # Make one small controller step easy to test before writing the
        # forever loop in run().
        #
        # Implementation guide:
        # 1. Create a FaceRenderer only when self.renderer is None.
        # 2. Read the latest state from self.face_state.get().
        # 3. Pass that state to self.renderer.draw(state).
        #
        # Expected return value:
        # Nothing. This method draws exactly one frame.
        return


    def run(self, sleep_seconds: float = 0.1) -> None:
        """Continuously render the face matching the latest FaceState.

        Inputs:
        - sleep_seconds: pause between frames. Reads self.face_state and uses
          self.renderer.

        Output:
        - None. This method keeps running until the program is stopped.
        """
        # Lesson 2: Face Controller
        #
        # Goal:
        # Keep the face display updated while the agent is doing other work.
        #
        # Concept to learn:
        # This method runs in a background thread. It should loop forever:
        # read the current state, draw that state's next frame, pause briefly,
        # and repeat.
        #
        # Suggested package:
        # - time.sleep: pause between frames.
        #
        # Implementation guide:
        # 1. Create a FaceRenderer when one was not supplied to __init__().
        # 2. Call self.renderer.load() once before the loop.
        # 3. Inside the loop, call self.run_once() to draw the latest state.
        # 4. Sleep for sleep_seconds so the loop does not use all CPU time.
        #
        # Expected return value:
        # Nothing. This method keeps running.
        return
