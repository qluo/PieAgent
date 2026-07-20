from face.renderer import FaceRenderer
from face.state import FaceState
import time


class FaceController:
    def __init__(self, face_state: FaceState, renderer: FaceRenderer | None = None) -> None:
        """Create the face controller.

        Inputs:
        - face_state: shared FaceState object. The agent writes states such as
          "listening" here, and this controller reads them to choose a face.
        - renderer: optional FaceRenderer that loads and draws image frames.
          Tests pass in a small fake renderer; in the real program, create a
          FaceRenderer when this value is None.

        Output:
        - None. The controller stores the inputs for later use.
        """
        # The controller reads this shared value to know which face to draw.
        self.face_state = face_state
        # A supplied renderer helps tests; run_once() creates one when this is None.
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
        if self.renderer is None:
            self.renderer = FaceRenderer()

        self.renderer.load()
        while True:
            self.run_once()
            time.sleep(sleep_seconds)
