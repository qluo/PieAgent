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
        # 1. Open the microphone with sounddevice.
        # 2. Feed short chunks of audio into openwakeword.
        # 3. Return from this method only when the wake score is high enough.
        #
        # Expected return value:
        # Nothing. This method returns only when the wake word is detected.
        # Lesson 3 helper functions:
        # - For keyboard practice, call self._wait_for_keyboard_wake().
        # - For the Raspberry Pi version, call self._wait_for_microphone_wake().
        # - Use self.mode to choose between "keyboard" and "microphone".
        
        if self.mode == "keyboard":
            self._wait_for_keyboard_wake()
            return

        if self.mode != "microphone":
            raise ValueError('WakeWordTool mode must be "microphone" or "keyboard".')

        self._wait_for_microphone_wake()

    def _wait_for_keyboard_wake(self) -> None:
        """Teaching helper: wait until someone types wake."""
        # Implementation guide:
        # 1. Keep asking for input in a loop.
        # 2. Strip spaces and convert the typed text to lowercase.
        # 3. Return only when the normalized word is "wake".
        while True:
            typed_word = input("Type 'wake' to wake PiAgent: ").strip().lower()
            if typed_word == "wake":
                return

    def _wait_for_microphone_wake(self) -> None:
        """Listen to microphone audio and check openWakeWord scores."""
        # Implementation guide:
        # 1. Load the openWakeWord Model.
        # 2. Create audio_queue = Queue().
        # 3. Make audio_callback(indata, _frames, _time, status). Inside it, add
        #    one mono audio chunk with audio_queue.put(indata[:, 0].copy()).
        # 4. Open sd.InputStream(..., callback=audio_callback).
        # 5. In a loop, score each chunk with model.predict(audio_chunk).
        # 6. Return when max(scores.values()) reaches self.threshold.
        
        if self.model_path:
            model = Model(wakeword_models=[self.model_path])
        else:
            model = Model()

        audio_queue: Queue = Queue()

        def audio_callback(indata, _frames, _time, status) -> None:
            if status:
                print(f"Microphone status: {status}")
            audio_queue.put(indata[:, 0].copy())

        print("Listening for wake word...")
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=CHUNK_SIZE,
            callback=audio_callback,
        ):
            while True:
                audio_chunk = audio_queue.get()
                scores = model.predict(audio_chunk)
                if scores and max(scores.values()) >= self.threshold:
                    return
