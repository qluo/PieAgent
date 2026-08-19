from collections import deque
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
        pre_roll_seconds: float = 0.3,
        engine: str = "whisper",
        parakeet_model_dir: str = "models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8",
        parakeet_threads: int = 4,
    ) -> None:
        """Create a Whisper.cpp or Sherpa-ONNX Parakeet speech-to-text tool."""
        self.sample_rate = sample_rate
        self.max_seconds = max_seconds
        self.silence_seconds = silence_seconds
        self.model_path = model_path
        self.whisper_binary = whisper_binary
        self.mode = mode
        self.pre_roll_seconds = pre_roll_seconds
        if engine not in {"whisper", "parakeet"}:
            raise ValueError('STT engine must be "whisper" or "parakeet".')
        self.engine = engine
        self.parakeet_model_dir = Path(parakeet_model_dir)
        self.parakeet_threads = parakeet_threads
        self._parakeet_recognizer = None

    def listen_and_transcribe(self) -> str:
        """Listen to the user and return the words as text."""
        if self.mode == "keyboard":
            return input("You: ")

        audio = self.listen_until_silence()
        text = self.transcribe(audio)

        print(f"Heard: {text}")
        return text

    def transcribe(self, audio: bytes) -> str:
        """Transcribe captured 16-bit mono audio with the selected backend."""
        if self.engine == "parakeet":
            return self.run_parakeet(audio)

        wav_path = self.save_temp_wav(audio)
        try:
            return self.run_whisper(wav_path)
        finally:
            wav_path.unlink(missing_ok=True)

    def listen_until_silence(self) -> bytes:
        """Record when someone speaks, then stop after a short silence."""
        import sounddevice as sd

        chunk_seconds = 0.1
        chunk_size = int(self.sample_rate * chunk_seconds)
        speech_threshold = 500
        max_chunks = int(self.max_seconds / chunk_seconds)
        quiet_chunks_needed = int(self.silence_seconds / chunk_seconds)

        chunks = []
        pre_roll_chunks = deque(maxlen=int(self.pre_roll_seconds / chunk_seconds))
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
                pre_roll_chunks.append(chunk_bytes)
                is_speech = self.loudness(chunk_bytes) > speech_threshold

                if is_speech and not speech_started:
                    speech_started = True
                    chunks.extend(pre_roll_chunks)
                    quiet_chunks = 0
                elif speech_started:
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

    def run_parakeet(self, audio: bytes) -> str:
        """Transcribe audio with the cached local Parakeet TDT INT8 recognizer."""
        import numpy as np

        recognizer = self._get_parakeet_recognizer()
        samples = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
        stream = recognizer.create_stream()
        stream.accept_waveform(self.sample_rate, samples)
        recognizer.decode_stream(stream)
        return stream.result.text.strip()

    def _get_parakeet_recognizer(self):
        if self._parakeet_recognizer is not None:
            return self._parakeet_recognizer

        required_files = ("encoder.int8.onnx", "decoder.int8.onnx", "joiner.int8.onnx", "tokens.txt")
        if not all((self.parakeet_model_dir / name).is_file() for name in required_files):
            raise RuntimeError(
                "Parakeet model files are missing. Download the model described in docs/setup.md."
            )
        try:
            import sherpa_onnx
        except ImportError as error:
            raise RuntimeError(
                "Missing Sherpa-ONNX package. Run: uv pip install -r requirements.txt"
            ) from error

        self._parakeet_recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(self.parakeet_model_dir / "encoder.int8.onnx"),
            decoder=str(self.parakeet_model_dir / "decoder.int8.onnx"),
            joiner=str(self.parakeet_model_dir / "joiner.int8.onnx"),
            tokens=str(self.parakeet_model_dir / "tokens.txt"),
            num_threads=self.parakeet_threads,
            sample_rate=self.sample_rate,
            decoding_method="greedy_search",
            provider="cpu",
            model_type="nemo_transducer",
        )
        return self._parakeet_recognizer
