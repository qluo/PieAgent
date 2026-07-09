from face import states
from face.state import FaceState


class Agent:
    def __init__(
        self,
        face_state: FaceState,
        wake_word: object,
        stt: object,
        tts: object,
        llm: object,
        tools: dict[str, object],
    ) -> None:
        """Create the agent.

        Inputs:
        - face_state: shared FaceState used to tell the face controller what
          the agent is doing.
        - wake_word: tool object with wait() -> None.
        - stt: tool object with listen_and_transcribe() -> str.
        - tts: tool object with speak(text: str) -> None.
        - llm: tool object with answer(user_text: str) -> str.
        - tools: optional extra tools, such as {"search": SearchTool()}.

        Output:
        - None. The new Agent stores these objects for later use.
        """
        self.face_state = face_state
        self.wake_word = wake_word
        self.stt = stt
        self.tts = tts
        self.llm = llm
        self.tools = tools

    def run(self) -> None:
        """Run the main agentic loop.

        Inputs:
        - None directly. This method uses the tools passed into __init__().

        Output:
        - None. This method keeps running until the program is stopped.

        Side effects:
        - Changes face_state.
        - Waits for wake word.
        - Records/transcribes speech.
        - Speaks the answer.
        """
        while True:
            self.face_state.set(states.IDLE)
            self.wake_word.wait()

            self.face_state.set(states.LISTENING)
            user_text = self.stt.listen_and_transcribe()

            self.face_state.set(states.THINKING)
            response = self.respond(user_text)

            self.face_state.set(states.SPEAKING)
            self.tts.speak(response)

    def respond(self, user_text: str) -> str:
        """Produce a response, optionally using tools.

        Inputs:
        - user_text: the user's question or command as text.

        Output:
        - A response string that can be sent to self.tts.speak(...).
        """
        return self.llm.answer(user_text)
