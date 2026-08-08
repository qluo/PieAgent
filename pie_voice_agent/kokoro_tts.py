import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path


class KokoroTextToSpeechTool:
    """Speak local Kokoro TTS audio through the system audio player."""

    def __init__(
        self,
        model_path: str = "models/kokoro/kokoro-v0_19.onnx",
        voices_path: str = "models/kokoro/voices.json",
        voice: str = "af_sarah",
        speed: float = 1.0,
        language: str = "en-us",
        player_binary: str | None = None,
    ) -> None:
        """Load a local Kokoro model and configure its voice."""
        self.model_path = Path(model_path)
        self.voices_path = Path(voices_path)
        self.voice = voice
        self.speed = speed
        self.language = language
        self.player_binary = player_binary or (
            "afplay" if sys.platform == "darwin" else "aplay"
        )
        self.kokoro = self._load_model()

    def speak(
        self, text: str, on_playback_started: Callable[[], None] | None = None
    ) -> None:
        """Generate and play speech for ``text``."""
        samples, sample_rate = self.kokoro.create(
            text,
            voice=self.voice,
            speed=self.speed,
            lang=self.language,
        )
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as file:
            audio_path = Path(file.name)

        try:
            import soundfile as sf

            sf.write(audio_path, samples, sample_rate)
            if on_playback_started is not None:
                on_playback_started()
            subprocess.run([self.player_binary, str(audio_path)], check=True)
        finally:
            audio_path.unlink(missing_ok=True)

    def _load_model(self):
        if not self.model_path.is_file() or not self.voices_path.is_file():
            raise RuntimeError(
                "Kokoro model files are missing. Download the model and voices files "
                "described in docs/setup.md."
            )

        try:
            from kokoro_onnx import Kokoro
        except ImportError as error:
            raise RuntimeError(
                "Missing Kokoro packages. Run: uv pip install -r requirements.txt"
            ) from error

        return Kokoro(str(self.model_path), str(self.voices_path))
