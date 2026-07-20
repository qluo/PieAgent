import queue
import subprocess
import tempfile
import wave
from pathlib import Path

import sounddevice as sd


class SpeechToTextTool:
    def __init__(
        self,
        sample_rate: int = 16000,
        seconds: float = 10.0,
        silence_seconds: float = 0.9,
        silence_threshold: int = 500,
        model_path: str = "./models/ggml-base.en.bin",
        whisper_binary: str = "./whisper.cpp/build/bin/whisper-cli",
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
        # The microphone records this many audio samples every second.
        self.sample_rate = sample_rate
        # Recording stops after this maximum number of seconds.
        self.seconds = seconds
        # After speech starts, this much quiet ends the recording.
        self.silence_seconds = silence_seconds
        # Chunks louder than this average value count as speech.
        self.silence_threshold = silence_threshold
        # whisper.cpp loads this local model to turn audio into words.
        self.model_path = model_path
        # This command runs whisper.cpp on the temporary WAV file.
        self.whisper_binary = whisper_binary
        # Keyboard mode avoids microphone hardware while students test the loop.
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
        # Implementation guide:
        # 1. Call self.listen_until_silence() to capture one spoken question.
        # 2. Inside listen_until_silence(), call self.loudness(audio_chunk) to
        #    decide when speech starts and when silence has lasted long enough.
        # 3. Save the recorded audio bytes as a temporary WAV file.
        # 4. Run whisper.cpp using self.whisper_binary and self.model_path.
        # 5. Delete the temporary WAV after whisper.cpp finishes.
        # 6. Print and return the transcription text.
        #
        # Expected return value:
        # The user's words as a Python string.
        if self.mode == "keyboard":
            return input("You: ")

        audio = self.listen_until_silence()
        wav_path = self.save_temp_wav(audio)
        text = self.run_whisper(wav_path)
        wav_path.unlink(missing_ok=True)

        print(f"Heard: {text}")
        return text

    def save_temp_wav(self, audio: bytes) -> Path:
        """Save microphone audio to a temporary WAV for whisper.cpp."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            wav_path = Path(temp_file.name)

        with wave.open(str(wav_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio)

        return wav_path

    def run_whisper(self, wav_path: Path) -> str:
        """Ask whisper.cpp to transcribe the WAV file."""
        command = [
            self.whisper_binary,
            "-m",
            self.model_path,
            "-f",
            str(wav_path),
            "-nt",
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True)

        lines = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("[") and "]" in line:
                line = line.split("]", 1)[1].strip()
            if line:
                lines.append(line)

        return " ".join(lines).strip()

    def listen_until_silence(self) -> bytes:
        """Record when speech starts, then stop after a short silence."""
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
