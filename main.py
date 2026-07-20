from threading import Thread

from agent.agent import Agent
from agent.tools.llm import LlmTool
from agent.tools.search import SearchTool
from agent.tools.stt import SpeechToTextTool
from agent.tools.tts import TextToSpeechTool
from agent.tools.wake_word import WakeWordTool
from face.controller import FaceController
from face.state import FaceState


def main() -> None:
    """Start the face controller and agent.

    Inputs:
    - None. Creates all objects inside the function.

    Output:
    - None. Runs until the agent program is stopped.
    """
    # Lesson 10: Put Everything Together
    #
    # Implementation guide:
    # 1. Create one shared FaceState.
    # 2. Give it to FaceController and start controller.run() in a daemon
    #    Thread so face drawing continues while the agent waits for input.
    # 3. Create Agent with the same FaceState, WakeWordTool,
    #    SpeechToTextTool, TextToSpeechTool, LlmTool, and a "search" tool.
    # 4. Start the completed agent with agent.run().
    return


if __name__ == "__main__":
    main()
