DEFAULT_WAKE_WORD_MODEL = "hey_jarvis"
CHUNK_SIZE = 1280

from queue import Queue

import sounddevice as sd
from openwakeword.model import Model


class WakeWordTool:
    def __init__(
        self,
        model_path: str | None = DEFAULT_WAKE_WORD_MODEL,
        threshold: float = 0.5,
        sample_rate: int = 16000,
        mode: str = "microphone",
    ) -> None:
        """Create the wake word tool.

        Inputs:
        - model_path: openWakeWord model name or optional path to a model file.
        - threshold: score needed before the wake word counts as detected.
        - sample_rate: microphone sample rate expected by the wake model.
        - mode: "keyboard" for the classroom/test version or "microphone" for
          live Raspberry Pi audio. It defaults to "microphone" for the real
          assistant.

        Output:
        - None. Stores settings for wait().
        """
        # openWakeWord loads this model name or model file to listen for.
        self.model_path = model_path
        # A model score must reach this value before wake detection succeeds.
        self.threshold = threshold
        # The microphone must provide audio at this rate for the wake model.
        self.sample_rate = sample_rate
        # Keyboard mode is for lessons; microphone mode listens to live audio.
        self.mode = mode

    def wait(self) -> None:
        """Block until the wake word is detected.

        Inputs:
        - None. A real version listens to the microphone using settings from
          __init__().

        Output:
        - None. Returns only after the wake word is detected.
        """
        # Lesson 3: Wake Word Detection
        #
        # Goal:
        # Pause here until the assistant should wake up.
        #
        # Suggested packages:
        # - openwakeword: detects wake words from microphone audio.
        # - sounddevice: records microphone audio in Python.
        # - numpy<2: audio arrays used by openwakeword.
        #
        # Implementation guide:
        # 1. Check self.mode.
        # 2. In keyboard mode, call the keyboard helper and return when it ends.
        # 3. In microphone mode, call the microphone helper.
        # 4. Raise a clear ValueError for any other mode so configuration errors
        #    are found before recording starts.
        #
        # Expected return value:
        # Nothing. This method returns only when the wake word is detected.
        return

    def _wait_for_keyboard_wake(self) -> None:
        """Teaching helper: wait until someone types wake."""
        # Implementation guide:
        # 1. Keep asking for input in a loop.
        # 2. Strip spaces and convert the typed text to lowercase.
        # 3. Return only when the normalized word is "wake".
        return

    def _wait_for_microphone_wake(self) -> None:
        """Listen to microphone audio and check openWakeWord scores."""
        # Implementation guide:
        # 1. Load Model with self.model_path when it has a value; otherwise,
        #    create the default openWakeWord model.
        # 2. Create a Queue to pass microphone chunks from the callback to the
        #    scoring loop.
        # 3. Write a callback that reports a status when present, then adds a
        #    copied mono chunk from indata[:, 0] to the queue.
        # 4. Open sd.InputStream with self.sample_rate, one channel, int16
        #    audio, CHUNK_SIZE, and that callback.
        # 5. In the stream, get one chunk at a time and score it with
        #    model.predict(audio_chunk).
        # 6. Return when a score reaches self.threshold.
        return
