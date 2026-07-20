from pathlib import Path
from face import states
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
        # The agent writes its current activity here for the face controller.
        self.face_state = face_state
        # This tool blocks until the student wakes the agent.
        self.wake_word = wake_word
        # This tool turns the next spoken question into text.
        self.stt = stt
        # This tool says the completed answer out loud.
        self.tts = tts
        # This tool creates answers and decides whether a search is useful.
        self.llm = llm
        # Extra named tools, such as the search tool used in respond().
        self.tools = tools
        # Read the default instructions once instead of opening AGENTS.md every turn.
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
        # Implementation guide:
        # 1. Set the face to idle before waiting for a wake word.
        # 2. After wake_word.wait() returns, set the face to listening and ask
        #    the STT tool for the user's words.
        # 3. Set the face to thinking while respond(user_text) creates an answer.
        # 4. Set the face to speaking before sending the answer to the TTS tool.
        # 5. Repeat the whole sequence so the agent can handle another request.
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
        # Implementation steps for Lessons 8 and 9:
        # 1. Build one LLM prompt from the user's text and AGENTS.md.
        # 2. When a search tool and needs_search() are available, ask the LLM
        #    whether the prompt needs current information.
        # 3. If it does, search with the original user text, then pass both the
        #    prompt and search context to answer_with_context().
        # 4. Otherwise, return the direct answer from answer(prompt).
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
        # Implementation guide:
        # 1. Treat whitespace-only instructions as missing instructions.
        # 2. When no instructions exist, return user_text unchanged.
        # 3. Otherwise, make a prompt with labeled instruction and user-request
        #    sections so the model can tell them apart.
        #
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
        # Implementation guide:
        # 1. Build the file path from PROJECT_ROOT and "AGENTS.md".
        # 2. Return an empty string when the optional file is missing.
        # 3. Otherwise read and return its UTF-8 text.
        #
        agents_file = PROJECT_ROOT / "AGENTS.md"
        if not agents_file.is_file():
            return ""
        return agents_file.read_text(encoding="utf-8")
