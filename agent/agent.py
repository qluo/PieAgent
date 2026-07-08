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
        pass

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
        # If the user says "search" or "look up", call:
        #   self.tools["search"].search(user_text)
        # Then pass the search result into:
        #   self.llm.answer_with_context(user_text, context)
        #
        # Expected return value:
        # A string that can be sent to self.tts.speak(...).
        return ""
