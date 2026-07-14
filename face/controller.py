from face.renderer import FaceRenderer
from face.state import FaceState


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
        # Keep the shared state and drawing tool together for run_once() and run().
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
        # Small first step:
        # 1. Read the current state with self.face_state.get().
        # 2. Call self.renderer.draw(state).
        #
        # Expected return value:
        # Nothing. This method draws exactly one frame.
        pass

    def run(self, sleep_seconds: float = 0.1) -> None:
        """Continuously render the face matching the latest FaceState.

        Inputs:
        - None directly. Reads self.face_state and uses self.renderer.

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
        # Small first step:
        # Print the current state whenever it changes.
        #
        # Real version idea:
        # 1. Call self.renderer.load() once before the loop.
        # 2. Inside the loop, call self.run_once().
        # 3. Sleep for a short time, such as 0.1 seconds.
        #
        # Expected return value:
        # Nothing. This method keeps running.
        pass
