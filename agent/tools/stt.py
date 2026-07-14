class SpeechToTextTool:
    def __init__(
        self,
        sample_rate: int = 16000,
        seconds: float = 10.0,
        silence_seconds: float = 0.9,
        silence_threshold: int = 500,
        model_path: str = "models/ggml-base.en.bin",
        whisper_binary: str = "whisper.cpp/build/bin/whisper-cli",
        mode: str = "microphone",
    ) -> None:
        """Create the speech-to-text tool.

        Inputs:
        - sample_rate: microphone sample rate for recording.
        - seconds: maximum listening time.
        - silence_seconds: how long quiet must last before recording stops.
        - silence_threshold: loudness needed before a chunk counts as speech.
        - model_path: whisper.cpp model file path.
        - whisper_binary: whisper.cpp command path.
        - mode: "keyboard" for early tests, "microphone" for the Pi version.

        Output:
        - None. Stores settings for listen_and_transcribe().
        """
        self.sample_rate = sample_rate
        self.seconds = seconds
        self.silence_seconds = silence_seconds
        self.silence_threshold = silence_threshold
        self.model_path = model_path
        self.whisper_binary = whisper_binary
        self.mode = mode

    def listen_and_transcribe(self) -> str:
        """Capture user speech and return transcribed text.

        Inputs:
        - None. A real version records audio using settings from __init__().

        Output:
        - The user's words as a string.
        """
        # Lesson 5: Speech-To-Text
        #
        # Goal:
        # Record the user's voice and turn it into text.
        #
        # Suggested packages/tools:
        # - sounddevice: record audio from the microphone.
        # - numpy<2: stores recorded audio arrays.
        # - wave: built-in Python module for saving WAV files.
        # - whisper.cpp: local speech-to-text program for transcription.
        #
        # Small first step:
        # If self.mode is "keyboard", return input("You: ") so the rest of the
        # agent can be tested before the microphone works.
        #
        # Real version idea:
        # 1. Call self.listen_until_silence() to capture one spoken question.
        # 2. Inside listen_until_silence(), call self.loudness(audio_chunk) to
        #    decide when speech starts and when silence has lasted long enough.
        # 3. Save the recorded audio bytes as a temporary WAV file.
        # 4. Run whisper.cpp using self.whisper_binary and self.model_path.
        # 5. Return the transcription text from whisper.cpp.
        #
        # Expected return value:
        # The user's words as a Python string.
        return ""

    def listen_until_silence(self) -> bytes:
        """Record when speech starts, then stop after a short silence."""
        import queue

        import sounddevice as sd

        chunk_seconds = 0.1
        chunk_size = int(self.sample_rate * chunk_seconds)
        quiet_chunks_needed = int(self.silence_seconds / chunk_seconds)
        max_chunks = int(self.seconds / chunk_seconds)
        audio_queue: queue.Queue[bytes] = queue.Queue()

        def callback(indata, _frames, _time, _status) -> None:
            audio_queue.put(bytes(indata))

        recorded_chunks: list[bytes] = []
        heard_speech = False
        quiet_chunks = 0

        with sd.RawInputStream(
            channels=1,
            samplerate=self.sample_rate,
            blocksize=chunk_size,
            dtype="int16",
            callback=callback,
        ):
            for _ in range(max_chunks):
                chunk = audio_queue.get()
                is_speech = self.loudness(chunk) > self.silence_threshold

                if is_speech:
                    heard_speech = True
                    quiet_chunks = 0

                if heard_speech:
                    recorded_chunks.append(chunk)
                    if not is_speech:
                        quiet_chunks += 1
                    if quiet_chunks >= quiet_chunks_needed:
                        break

        return b"".join(recorded_chunks)

    def loudness(self, audio_bytes: bytes) -> float:
        """Return a simple average volume for 16-bit microphone audio."""
        if not audio_bytes:
            return 0.0

        total = 0
        sample_count = 0
        for index in range(0, len(audio_bytes) - 1, 2):
            sample = int.from_bytes(audio_bytes[index : index + 2], "little", signed=True)
            total += abs(sample)
            sample_count += 1

        if sample_count == 0:
            return 0.0
        return total / sample_count
