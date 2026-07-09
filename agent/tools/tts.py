import subprocess


class TextToSpeechTool:
    def __init__(
        self,
        voice_model_path: str,
        piper_binary: str = "piper",
        player_binary: str = "aplay",
        sample_rate: int = 22050,
    ) -> None:
        """Create the text-to-speech tool."""
        self.voice_model_path = voice_model_path
        self.piper_binary = piper_binary
        self.player_binary = player_binary
        self.sample_rate = sample_rate

    def speak(self, text: str) -> None:
        """Speak text aloud with Piper."""
        # Piper reads text from stdin and writes raw speech audio to stdout.
        # We use --output-raw so the audio can go straight to the speaker.
        piper = subprocess.Popen(
            [
                self.piper_binary,
                "--model",
                self.voice_model_path,
                "--output-raw",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        # aplay reads the raw audio from Piper and sends it to the speaker.
        # These settings match Piper's common 16-bit mono output format.
        player = subprocess.Popen(
            [
                self.player_binary,
                "-r",
                str(self.sample_rate),
                "-f",
                "S16_LE",
                "-t",
                "raw",
                "-",
            ],
            stdin=piper.stdout,
        )

        # Close our extra copy of Piper's stdout so aplay knows when audio ends.
        if piper.stdout is not None:
            piper.stdout.close()

        # Send the sentence to Piper, then wait for speech generation and playback.
        if piper.stdin is not None:
            piper.stdin.write(text.encode("utf-8"))
            piper.stdin.close()

        piper.wait()
        player.wait()
