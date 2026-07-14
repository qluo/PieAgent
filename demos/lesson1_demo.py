from threading import Lock, Thread
from time import sleep


class FaceState:
    def __init__(self) -> None:
        """Create shared face state.

        Inputs: none.
        Output: none. Starts with the "idle" state.
        """
        self._state = "idle"
        self._lock = Lock()

    def set(self, state: str) -> None:
        """Set the current face state.

        Input: state, such as "idle", "listening", or "thinking".
        Output: none.
        """
        with self._lock:
            self._state = state

    def get(self) -> str:
        """Get the current face state.

        Inputs: none.
        Output: the current face state string.
        """
        with self._lock:
            return self._state


class FaceController:
    FACES = {
        "idle": "( -_- )",
        "listening": "( o_o )",
        "thinking": "( ?_? )",
        "speaking": "( ^_^ )",
        "error": "( x_x )",
    }

    def __init__(self, face_state: FaceState) -> None:
        """Create the fake face controller.

        Input: face_state, the shared FaceState to read.
        Output: none.
        """
        self.face_state = face_state
        self.last_state = None

    def run(self) -> None:
        """Print a fake face whenever the state changes.

        Inputs: none directly. Reads self.face_state.
        Output: none. Keeps running until the program stops.
        """
        while True:
            state = self.face_state.get()

            if state != self.last_state:
                face = self.FACES.get(state, self.FACES["error"])
                print(f"\nFace: {face}  {state}")
                self.last_state = state

            sleep(0.1)


class FakeWakeWordTool:
    def wait(self) -> None:
        """Wait for the fake wake word.

        Inputs: none.
        Output: none. Returns after the user presses Enter.
        """
        input("\nPress Enter to wake the agent...")


class FakeSpeechToTextTool:
    def listen_and_transcribe(self) -> str:
        """Get fake speech input from the keyboard.

        Inputs: none.
        Output: the typed user text.
        """
        return input("You: ")


class FakeLlmTool:
    def answer(self, user_text: str) -> str:
        """Create a fake LLM answer.

        Input: user_text, the user's typed question.
        Output: the fake agent response string.
        """
        text = user_text.lower()

        if "name" in text:
            return "My name is Pi Agent."

        if "hello" in text or "hi" in text:
            return "Hello! I am awake and ready."

        if "joke" in text:
            return "Why did the computer get cold? It forgot to close Windows."

        return f"You said: {user_text}"


class FakeTextToSpeechTool:
    def speak(self, text: str) -> None:
        """Fake speech by printing text.

        Input: text, the sentence the agent should say.
        Output: none.
        """
        print(f"Agent: {text}")
        sleep(1)


class Agent:
    def __init__(
        self,
        face_state: FaceState,
        wake_word: FakeWakeWordTool,
        stt: FakeSpeechToTextTool,
        llm: FakeLlmTool,
        tts: FakeTextToSpeechTool,
    ) -> None:
        """Create the fake agent.

        Inputs:
        - face_state: shared state that tells the fake face which expression to
          show.
        - wake_word: fake tool that waits for the user to press Enter.
        - stt: fake speech-to-text tool that returns typed text.
        - llm: fake language-model tool that returns prepared answers.
        - tts: fake text-to-speech tool that prints the answer.

        Output: none.
        """
        self.face_state = face_state
        self.wake_word = wake_word
        self.stt = stt
        self.llm = llm
        self.tts = tts

    def run(self) -> None:
        """Run the fake agent loop.

        Inputs: none directly. Uses the tools passed into __init__().
        Output: none. Stops when the user types quit, exit, or stop.
        """
        print("Pi Agent demo is running. Type 'quit' when asked to speak.")

        while True:
            self.face_state.set("idle")
            self.wake_word.wait()

            self.face_state.set("listening")
            user_text = self.stt.listen_and_transcribe()

            if user_text.lower() in ["quit", "exit", "stop"]:
                self.face_state.set("idle")
                print("Goodbye!")
                break

            self.face_state.set("thinking")
            response = self.llm.answer(user_text)

            self.face_state.set("speaking")
            self.tts.speak(response)


def main() -> None:
    """Start the fake face controller and fake agent.

    Inputs: none.
    Output: none.
    """
    face_state = FaceState()

    face_controller = FaceController(face_state)
    Thread(target=face_controller.run, daemon=True).start()

    agent = Agent(
        face_state=face_state,
        wake_word=FakeWakeWordTool(),
        stt=FakeSpeechToTextTool(),
        llm=FakeLlmTool(),
        tts=FakeTextToSpeechTool(),
    )
    agent.run()


if __name__ == "__main__":
    main()
