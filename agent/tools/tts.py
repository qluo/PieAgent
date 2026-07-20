import subprocess


class TextToSpeechTool:
    def __init__(
        self,
        voice_model_path: str = "models/piper/en_US-lessac-low.onnx",
        piper_binary: str = "tools/piper/piper",
        player_binary: str = "aplay",
        sample_rate: int = 22050,
    ) -> None:
        """Store the settings used by :meth:`speak`.

        Args:
            voice_model_path: Local Piper voice model.
            piper_binary: Piper command that turns text into raw audio.
            player_binary: Audio-player command that sends raw audio to the speaker.
            sample_rate: Sample rate used by the voice and aplay.
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
        # Implementation guide:
        # 1. Start Piper with the selected voice model, --output-raw, and pipes
        #    for its standard input and output.
        # 2. Start aplay with the selected sample rate and raw 16-bit mono
        #    audio settings. Give it Piper's stdout as its input.
        # 3. Encode text as UTF-8, write it to Piper's stdin, then close stdin
        #    to tell Piper there is no more text.
        # 4. Wait for both processes so the next agent turn does not start
        #    speaking before the current response has finished.
        
        return
