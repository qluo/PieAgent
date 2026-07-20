import subprocess


class TextToSpeechTool:
    def __init__(
        self,
        voice_model_path: str = "models/piper/en_US-lessac-low.onnx",
        piper_binary: str = "tools/piper/piper",
        player_binary: str = "aplay",
        sample_rate: int = 22050,
    ) -> None:
        """Create the text-to-speech tool.

        Inputs:
        - voice_model_path: path to a local Piper voice model.
        - piper_binary: path or command name for the Piper program.
        - player_binary: path or command name for the audio player.
        - sample_rate: audio sample rate expected by the Piper voice.

        Output:
        - None. Stores settings for speak().
        """
        # Piper loads this voice file to choose how Pie Agent sounds.
        self.voice_model_path = voice_model_path
        # This is the Piper program that converts text into raw audio.
        self.piper_binary = piper_binary
        # This is the audio player that sends Piper's audio to the speaker.
        self.player_binary = player_binary
        # aplay needs this value to play Piper's raw audio at the right speed.
        self.sample_rate = sample_rate

    def speak(self, text: str) -> None:
        """Speak text aloud.

        Inputs:
        - text: the sentence the agent should say.

        Output:
        - None. Returns after speaking or printing is finished.
        """
        # Lesson 6: Text-To-Speech
        #
        # Goal:
        # Turn the agent's response text into spoken audio.
        #
        # Suggested tools:
        # - Piper: local text-to-speech that can run on Raspberry Pi.
        # - aplay: simple WAV playback command on Raspberry Pi OS.
        #
        # Implementation guide:
        # 1. Start Piper with the selected voice model, --output-raw, and pipes
        #    for its standard input and output.
        # 2. Start aplay with the selected sample rate and raw 16-bit mono
        #    audio settings. Give it Piper's stdout as its input.
        # 3. Encode text as UTF-8, write it to Piper's stdin, then close stdin
        #    to tell Piper there is no more text.
        # 4. Wait for both processes so the next agent turn does not start
        #    speaking before the current response has finished.
        
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
        #if piper.stdout is not None:
        #    piper.stdout.close()

        # Send the sentence to Piper, then wait for speech generation and playback.
        if piper.stdin is not None:
            piper.stdin.write(text.encode("utf-8"))
            piper.stdin.close()

        piper.wait()
        player.wait()
