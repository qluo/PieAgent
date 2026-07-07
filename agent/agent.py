class Agent:
    def __init__(self, face_state, wake_word, stt, tts, llm, tools):
        self.face_state = face_state
        self.wake_word = wake_word
        self.stt = stt
        self.tts = tts
        self.llm = llm
        self.tools = tools

    def run(self):
        """Main agentic loop."""
        # TODO: Build the main agent loop here.
        # See demo.py for a simple working version.
        pass

    def respond(self, user_text: str) -> str:
        """Produce a response, optionally using tools."""
        # TODO: Decide how the agent should answer the user.
        return ""
