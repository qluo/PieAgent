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
    face_state = FaceState()

    face_controller = FaceController(face_state=face_state)
    Thread(target=face_controller.run, daemon=True).start()

    agent = Agent(
        face_state=face_state,
        wake_word=WakeWordTool(),
        stt=SpeechToTextTool(),
        tts=TextToSpeechTool(
            voice_model_path="models/piper/en_US-lessac-low.onnx",
        ),
        llm=LlmTool(),
        tools={
            "search": SearchTool(),
        },
    )
    agent.run()


if __name__ == "__main__":
    main()
