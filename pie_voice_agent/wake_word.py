from queue import Queue


CHUNK_SIZE = 1280
DEFAULT_WAKE_WORD_MODEL = "hey_jarvis"


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
        - mode: "microphone" for real audio, or "keyboard" for classroom tests.

        Output:
        - None. Stores settings for wait().
        """
        self.model_path = model_path
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.mode = mode

    def wait(self) -> None:
        """Block until the wake word is detected.

        Inputs:
        - None. A real version listens to the microphone using settings from
          __init__().

        Output:
        - None. Returns only after the wake word is detected.
        """
        if self.mode == "keyboard":
            self._wait_for_keyboard_wake()
            return

        if self.mode != "microphone":
            raise ValueError('WakeWordTool mode must be "microphone" or "keyboard".')

        self._wait_for_microphone_wake()

    def _wait_for_keyboard_wake(self) -> None:
        while True:
            typed_word = input("Type 'wake' to wake PiAgent: ").strip().lower()
            if typed_word == "wake":
                return

    def _wait_for_microphone_wake(self) -> None:
        try:
            import sounddevice as sd
            from openwakeword.model import Model
        except ImportError as error:
            raise RuntimeError(
                "Missing wake word audio packages. Run: uv pip install -r requirements.txt"
            ) from error

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
