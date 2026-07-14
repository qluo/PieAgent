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
        self.voice_model_path = voice_model_path
        self.piper_binary = piper_binary
        self.player_binary = player_binary
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
        # Small first step:
        # Print the text first:
        #   print(f"Agent: {text}")
        # Then replace the print with real speech after the loop works.
        #
        # Real version idea:
        # 1. Send text into Piper.
        # 2. Ask Piper for raw audio with --output-raw.
        # 3. Pipe Piper's raw audio directly into aplay.
        #
        # Expected return value:
        # Nothing. This method finishes after speaking is done.
        # Piper reads text from stdin and writes raw speech audio to stdout.
        # aplay reads that raw audio from stdin and sends it to the speaker.
        #
        # TODO for students:
        # 1. Start piper with subprocess.Popen(...).
        # 2. Send text into piper stdin.
        # 3. Pipe piper stdout into aplay stdin, without saving a WAV file.
        # 4. Wait for both programs to finish.
        pass
