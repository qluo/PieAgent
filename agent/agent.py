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
        """Create the agent and store its tools.

        Args:
            face_state: Shared state used to update the face controller.
            wake_word: Tool with ``wait()``.
            stt: Tool with ``listen_and_transcribe()``.
            tts: Tool with ``speak(text)``.
            llm: Tool with ``answer(user_text)``.
            tools: Extra named tools, such as ``{"search": SearchTool()}``.

        ``agents_md`` is loaded once here so every prompt can use the same
        project instructions without reading the file again.
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
        # Implementation guide:
        # 1. Set the face to idle before waiting for a wake word.
        # 2. After wake_word.wait() returns, set the face to listening and ask
        #    the STT tool for the user's words.
        # 3. Set the face to thinking while respond(user_text) creates an answer.
        # 4. Set the face to speaking before sending the answer to the TTS tool.
        # 5. Repeat the whole sequence so the agent can handle another request.
        #
        return

    def respond(self, user_text: str) -> str:
        """Produce a response, optionally using tools.

        Inputs:
        - user_text: the user's question or command as text.

        Output:
        - A response string that can be sent to self.tts.speak(...).
        """
        # Lesson 4, then later Lessons 8 and 9:
        #
        # Goal:
        # Decide whether the agent should answer directly with the LLM or use
        # a tool first.
        #
        # Implementation guide for Lesson 4:
        # 1. Return the direct answer from self.llm.answer(user_text).
        #
        # Later updates:
        # - Lesson 8 chooses between a direct answer and search context.
        # - Lesson 9 builds an AGENTS.md prompt for the LLM but keeps the
        #   original user_text for a search query.
        #
        # Lesson 8 update:
        # 1. Ask llm.needs_search(user_text) whether current search is useful.
        # 2. When it is, call the search tool and give its context to
        #    llm.answer_with_context(user_text, context).
        # 3. Otherwise, return the direct LLM answer.
        #
        # Lesson 9 update:
        # Build the LLM prompt first, but continue using the original user_text
        # as the search query.
        #
        # Expected return value:
        # A string that can be sent to self.tts.speak(...).

        return ""

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
        return ""

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
        return ""
