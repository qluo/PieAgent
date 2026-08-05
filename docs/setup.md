# Setup

## Test Pi Agent On A Mac

This is the recommended first run on macOS: it uses your keyboard for the wake
word and transcription, a local Ollama model for answers, and a local Kokoro
voice for speech. It does not need microphone permission or `whisper.cpp`.

Use macOS Sonoma (14) or later if possible. Apple Silicon gives the best local
LLM performance.

### 1. Install System Prerequisites

Install Xcode's command-line tools:

```bash
xcode-select --install
```

If you do not already have Homebrew, install it from [brew.sh](https://brew.sh).
Then install the audio libraries used by the microphone and Kokoro dependencies:

```bash
brew install portaudio espeak-ng
```

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen Terminal so `uv` is available, then confirm:

```bash
uv --version
```

### 2. Create The Python Environment

From the project folder—the folder containing `main.py` and
`requirements.txt`—run:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Install And Test Ollama

Download the macOS Ollama app from [ollama.com/download](https://ollama.com/download),
move it to Applications, and open it once. It makes the `ollama` command
available in Terminal.

The agent defaults to `gemma3:1b`, so download that model and check it works:

```bash
ollama pull gemma3:1b
ollama run gemma3:1b "Reply with OK."
```

Type `/bye` to leave Ollama's chat. If either command says `ollama` is not
found, quit and reopen the Ollama app, then open a new Terminal window.

### 4. Install And Test The Local Kokoro Voice

Download the small int8 Kokoro model and its voices once:

```bash
mkdir -p models/kokoro
curl -L -o models/kokoro/kokoro-v1.0.int8.onnx \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
curl -L -o models/kokoro/voices-v1.0.bin \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

Run the speech-only demo. You should hear one sentence through your Mac's
selected output device:

```bash
uv run python demos/kokoro_tts_demo.py
```

Kokoro is fully local after these files are downloaded. Its defaults are the
`af_sarah` voice and normal speed. You can preview another voice, for example:

```bash
PIE_AGENT_TTS_KOKORO_VOICE=af_bella uv run python demos/kokoro_tts_demo.py
```

### 5. Run The Agent In Keyboard Mode

This starts the real face, LLM, search routing, and Kokoro speech without
requiring the microphone stack:

```bash
export PIE_AGENT_TTS_ENGINE=kokoro
export PIE_AGENT_WAKE_WORD_MODE=keyboard
export PIE_AGENT_STT_MODE=keyboard
uv run python main.py
```

When prompted, type `wake`, then type a question such as `What is the capital
of France?`. The answer should appear in the terminal and be spoken. Stop the
agent with `Control-C`.

### 6. Optional: Use The Microphone Later

For microphone operation, give your terminal app microphone access in **System
Settings → Privacy & Security → Microphone**. Then remove the two keyboard
settings:

```bash
unset PIE_AGENT_WAKE_WORD_MODE PIE_AGENT_STT_MODE
```

The current microphone transcription tool also needs a local `whisper.cpp`
binary and a Whisper model at `models/ggml-base.en.bin`; those are not installed
by `requirements.txt`. Set those up before using microphone mode.

## Raspberry Pi Notes

The same Python setup applies on Raspberry Pi OS. Piper remains the default
TTS backend there and uses `aplay`; select Kokoro by setting
`PIE_AGENT_TTS_ENGINE=kokoro`. The current TTS tools choose `afplay` on macOS
and `aplay` on Linux automatically.

## Run Tests

Run from the project folder:

```bash
uv run pytest -q
```

The lesson folders can also be run individually, for example:

```bash
uv run pytest tests/lesson_6
```
