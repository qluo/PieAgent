import subprocess
import tempfile
import wave
from pathlib import Path


class SpeechToTextTool:
    def __init__(
        self,
        sample_rate: int = 16000,
        max_seconds: float = 10.0,
        silence_seconds: float = 1.0,
        model_path: str = "models/ggml-base.en.bin",
        whisper_binary: str = "whisper.cpp/build/bin/whisper-cli",
        mode: str = "microphone",
    ) -> None:
        """Create the speech-to-text tool."""
        self.sample_rate = sample_rate
        self.max_seconds = max_seconds
        self.silence_seconds = silence_seconds
        self.model_path = model_path
        self.whisper_binary = whisper_binary
        self.mode = mode

    def listen_and_transcribe(self) -> str:
        """Listen to the user and return the words as text."""
        if self.mode == "keyboard":
            return input("You: ")

        audio = self.listen_until_silence()
        wav_path = self.save_temp_wav(audio)
        text = self.run_whisper(wav_path)
        wav_path.unlink(missing_ok=True)

        print(f"Heard: {text}")
        return text

    def listen_until_silence(self) -> bytes:
        """Record when someone speaks, then stop after a short silence."""
        import sounddevice as sd

        chunk_seconds = 0.1
        chunk_size = int(self.sample_rate * chunk_seconds)
        speech_threshold = 500
        max_chunks = int(self.max_seconds / chunk_seconds)
        quiet_chunks_needed = int(self.silence_seconds / chunk_seconds)

        chunks = []
        quiet_chunks = 0
        speech_started = False

        print("Listening...")
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=chunk_size,
            dtype="int16",
            channels=1,
        ) as stream:
            for _ in range(max_chunks):
                chunk, _overflowed = stream.read(chunk_size)
                chunk_bytes = bytes(chunk)
                is_speech = self.loudness(chunk_bytes) > speech_threshold

                if is_speech:
                    speech_started = True
                    quiet_chunks = 0

                if speech_started:
                    chunks.append(chunk_bytes)
                    if is_speech:
                        quiet_chunks = 0
                    else:
                        quiet_chunks += 1

                if speech_started and quiet_chunks >= quiet_chunks_needed:
                    break

        return b"".join(chunks)

    def loudness(self, audio: bytes) -> float:
        """Return the average loudness of 16-bit microphone audio."""
        if not audio:
            return 0.0

        total = 0
        samples = len(audio) // 2
        for index in range(0, len(audio), 2):
            sample = int.from_bytes(audio[index : index + 2], "little", signed=True)
            total += abs(sample)

        return total / samples

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
