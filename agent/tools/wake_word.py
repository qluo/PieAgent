DEFAULT_WAKE_WORD_MODEL = "hey_jarvis"
CHUNK_SIZE = 1280


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
        - model_path: optional path to an openWakeWord model file.
        - threshold: score needed before the wake word counts as detected.
        - sample_rate: microphone sample rate expected by the wake model.
        - mode: "keyboard" for the classroom/test version or "microphone" for
          live Raspberry Pi audio. It defaults to "microphone" for the real
          assistant.

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
        # Small first step:
        # Do a keyboard version before real audio:
        # keep asking for input until the user types "wake".
        #
        # Real version idea:
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
        pass

    def _wait_for_keyboard_wake(self) -> None:
        """Teaching helper: wait until someone types wake."""
        # TODO for students:
        # 1. Keep asking for input().
        # 2. Return when the typed word is "wake".
        pass

    def _wait_for_microphone_wake(self) -> None:
        """Listen to microphone audio and check openWakeWord scores."""
        # TODO for students:
        # 1. Import Model from openwakeword.model, sounddevice as sd, and numpy
        #    as np.
        # 2. Create the wake word model once, before opening the microphone:
        #      model = Model(wakeword_models=[self.model_path])
        #    The default model name is "hey_jarvis". If you use a downloaded
        #    model, self.model_path can be its .onnx or .tflite file path.
        # 3. Make a variable such as detected = False. The callback will change
        #    it to True when the model hears the wake word.
        # 4. Write a callback with these four inputs. Its first line should be
        #    nonlocal detected so it can change the flag created outside it:
        #      def callback(indata, frames, time_info, status):
        #    If status is not empty, print it while debugging. The indata value
        #    is one short microphone chunk.
        # 5. Open sd.InputStream with samplerate=self.sample_rate, channels=1,
        #    dtype="int16", blocksize=CHUNK_SIZE, and callback=callback.
        #    openWakeWord expects 16-bit, 16 kHz, mono PCM samples. CHUNK_SIZE
        #    is 1280 samples, which is 80 ms at 16 kHz.
        # 6. Inside callback, make a one-dimensional NumPy array of int16 audio
        #    samples, for example: audio_chunk = indata[:, 0].copy().
        # 7. Score that chunk with prediction = model.predict(audio_chunk).
        #    prediction is a dictionary such as {"hey_jarvis": 0.82}. While
        #    debugging, print prediction so you can see the exact model key.
        # 8. Read the score for your model (or the largest score in prediction).
        #    If it is greater than or equal to self.threshold, set detected=True.
        # 9. Keep the InputStream open in a small loop until detected is True,
        #    then leave the with block and return. sd.sleep(100) is an easy way
        #    to keep the main thread alive while the callback receives audio.
        # 10. Keep this callback small: do not run STT, TTS, or the LLM here.
        #     Its only job is to score microphone chunks and notice the wake word.
        pass
