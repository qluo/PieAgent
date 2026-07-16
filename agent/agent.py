from pathlib import Path
from face.state import FaceState

PROJECT_ROOT = Path(__file__).resolve().parent.parent

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
        self.agents_md = self.load_agents_md()

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
        # Lesson 4: Implement The Main Agent Loop
        #
        # Goal:
        # Move the loop idea from demos/lesson1_demo.py into this clean Agent class.
        #
        # Concept to learn:
        # The Agent is the orchestrator. It decides the order of actions,
        # but each tool does its own special job.
        #
        # Small first step:
        # Copy the high-level shape from demos/lesson1_demo.py:
        # 1. Set face to "idle".
        # 2. Wait for wake word: self.wake_word.wait().
        # 3. Set face to "listening".
        # 4. Get user text: self.stt.listen_and_transcribe().
        # 5. Set face to "thinking".
        # 6. Get response: self.respond(user_text).
        # 7. Set face to "speaking".
        # 8. Speak response: self.tts.speak(response).
        #
        # Test idea:
        # Use fake tools first. If the loop works with fake tools, then swap
        # in one real tool at a time.
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
        # Lesson 4, then Lessons 7 and 8:
        #
        # Goal:
        # Decide whether the agent should answer directly with the LLM or use
        # a tool first.
        #
        # Small first step:
        # Return self.llm.answer(user_text).
        #
        # Later:
        # TODO for Lesson 8:
        # 1. Ask the LLM if search is needed:
        #      self.llm.needs_search(user_text)
        # 2. If the LLM says search is needed, call:
        #      self.tools["search"].search(user_text)
        # 3. Pass the search result into:
        #      self.llm.answer_with_context(user_text, context)
        # 4. If search is not needed, call:
        #      self.llm.answer(user_text)
        #
        # Lesson 9 update:
        # Start by calling self.build_prompt(user_text). Pass that prompt to
        # the LLM, but pass the original user_text to the search tool.
        #
        # Expected return value:
        # A string that can be sent to self.tts.speak(...).

        prompt = self.build_prompt(user_text)

        if (
            "search" in self.tools
            and hasattr(self.llm, "needs_search")
            and self.llm.needs_search(prompt)
        ):
            context = self.tools["search"].search(user_text)
            return self.llm.answer_with_context(prompt, context)

        return self.llm.answer(prompt)

    def build_prompt(self, user_text: str) -> str:
        """
        Combine persistent project instructions with a user request.
        Inputs:
        - user_text: the user's question or command.

        Output:
        - A prompt string for the LLM.
        """
        # Lesson 9: Local Agent Instructions
        #
        # Goal:
        # Keep Pi Agent's default behavior in AGENTS.md instead of repeating
        # it in every user request.
        #
        # Small first step:
        # If self.agents_md is empty, return user_text unchanged.
        # Otherwise, return a clear prompt containing both the instructions and
        # the user request.
        if not self.agents_md.strip():
            return user_text
        return (
            "Agent instructions:\n"
            f"{self.agents_md.strip()}\n\n"
            "User request:\n"
            f"{user_text}"
        )

    @staticmethod
    def load_agents_md() -> str:
        """Load the project's optional root AGENTS.md file.

        Output:
        - The file's text, or an empty string when the file is absent.
        """
        # Lesson 9: Local Agent Instructions
        #
        # Goal:
        # Read PROJECT_ROOT / "AGENTS.md" once when an Agent is created.
        #
        # Small first step:
        # 1. Build the path with PROJECT_ROOT / "AGENTS.md".
        # 2. Return "" when it is not a file.
        # 3. Otherwise return its UTF-8 text.
        agents_file = PROJECT_ROOT / "AGENTS.md"
        if not agents_file.is_file():
            return ""
        return agents_file.read_text(encoding="utf-8")
