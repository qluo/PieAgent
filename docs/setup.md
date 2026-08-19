# Setup

## Raspberry Pi Setup

This is the primary setup path. The Pi runs the voice application, calls a LAN-hosted Ollama model for reasoning and tools, and speaks locally with Kokoro. Start in keyboard mode; add the microphone after the full loop works.

### 1. Install System Dependencies

Use 64-bit Raspberry Pi OS. A desktop session is required for the animated face display.

```bash
sudo apt update
sudo apt install -y portaudio19-dev espeak-ng alsa-utils libsndfile1
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open a new terminal and confirm `uv --version` works.

### 2. Create The Python Environment

From the folder containing `main.py` and `requirements.txt`:

```bash
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Configure The Remote Ollama Model

Pie Agent uses Ollama's chat API for native tool calls. Set only the server base URL—do not include `/api/generate` or `/api/chat`:

```bash
export PIE_AGENT_OLLAMA_URL=http://192.168.68.69:11434
export PIE_AGENT_MODEL=qwen3.5:4b
# auto disables thinking for ordinary turns and enables it for explicit complex work.
export PIE_AGENT_THINKING=auto
curl -s "$PIE_AGENT_OLLAMA_URL/api/tags"
```

The JSON from `/api/tags` should show `qwen3.5:4b` with `tools` capability. On the model host, verify inference before continuing:

```bash
ollama run qwen3.5:4b "Reply with OK."
```

### 4. Install And Test Local Kokoro

Download the model and voices once:

```bash
mkdir -p models/kokoro
curl -L -o models/kokoro/kokoro-v0_19.onnx \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx
curl -L -o models/kokoro/voices.json \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.json

# Use the NumPy-1-compatible Kokoro asset pair, not v1 .bin voices files.
export PIE_AGENT_TTS_ENGINE=kokoro
export PIE_AGENT_TTS_KOKORO_MODEL=models/kokoro/kokoro-v0_19.onnx
export PIE_AGENT_TTS_KOKORO_VOICES=models/kokoro/voices.json

uv run python demos/kokoro_tts_demo.py
```

Kokoro is fully local after this download. Pie Agent uses `kokoro-onnx==0.3.0` with NumPy 1 because `openwakeword` is not compatible with NumPy 2. This Kokoro release requires the matching `kokoro-v0_19.onnx` and `voices.json` files; it cannot use the newer v1 `.bin` voices file. Its default voice is `af_sarah`; try `PIE_AGENT_TTS_KOKORO_VOICE=af_bella uv run python demos/kokoro_tts_demo.py` for another voice.

### 5. Download The Wake-Word Model

After keyboard mode works:

```bash
uv run python -c "import openwakeword; openwakeword.utils.download_models()"
```

This one-time download installs the bundled `hey_jarvis` wake-word model needed for microphone mode.

### 6. Add The Microphone

```bash
unset PIE_AGENT_WAKE_WORD_MODE PIE_AGENT_STT_MODE
git clone https://github.com/ggerganov/whisper.cpp
cmake -S whisper.cpp -B whisper.cpp/build
cmake --build whisper.cpp/build -j
./whisper.cpp/models/download-ggml-model.sh small.en
cp whisper.cpp/models/ggml-small.en.bin models/
export PIE_AGENT_STT_MODEL=models/ggml-small.en.bin
uv run python main.py
```

`small.en` is the recommended English model for a Raspberry Pi 5 with 4 GB or more RAM. It is more accurate than `base.en`, but slower and uses about 852 MB of memory. On a lower-memory Pi, download `base.en` instead and set `PIE_AGENT_STT_MODEL=models/ggml-base.en.bin`. The recorder keeps 300 ms of pre-speech audio so it does not clip the first word. The wake-word and STT adapters now use the Pi microphone; Kokoro uses `aplay` for local playback.

### 7. Optional: Test Quantized Whisper Small

`small.en-q5_1` is a quantized version of Whisper Small English. It uses less storage and memory than full `small.en` while aiming to retain similar recognition quality. Download it and select it for the current terminal session:

```bash
curl -L -o models/ggml-small.en-q5_1.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en-q5_1.bin
export PIE_AGENT_STT_MODEL=models/ggml-small.en-q5_1.bin
uv run python main.py
```

Compare it using the same spoken phrases as full `small.en`. To return to the faster base model, run:

```bash
export PIE_AGENT_STT_MODEL=models/ggml-base.en.bin
uv run python main.py
```

## Package Layout

- `pie_ai`: provider-neutral model messages, tool schemas, events, and `OllamaClient`.
- `pie_agent_core`: conversation, context, native tool loop, and lifecycle events.
- `pie_voice_agent`: wake word, STT, TTS, face, Markdown memory, and presentation.

The older lesson tests are retired teaching artifacts for the removed `agent/` package and are not the runtime acceptance suite.

## macOS Setup

For Mac keyboard-mode development, install prerequisites:

```bash
xcode-select --install
brew install portaudio espeak-ng
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Use the same remote-Ollama and Kokoro steps above. macOS uses `afplay` for local audio. For microphone use, grant the terminal app access in **System Settings → Privacy & Security → Microphone**, then follow the same `whisper.cpp` steps from the Raspberry Pi section.

## Keyboard-Mode Validation

Use this final check on either Raspberry Pi or macOS before troubleshooting microphone hardware:

```bash
export PIE_AGENT_OLLAMA_URL=http://192.168.68.69:11434
export PIE_AGENT_MODEL=qwen3.5:4b
export PIE_AGENT_THINKING=auto
export PIE_AGENT_TTS_ENGINE=kokoro
export PIE_AGENT_TTS_KOKORO_MODEL=models/kokoro/kokoro-v0_19.onnx
export PIE_AGENT_TTS_KOKORO_VOICES=models/kokoro/voices.json
export PIE_AGENT_WAKE_WORD_MODE=keyboard
export PIE_AGENT_STT_MODE=keyboard
uv run python main.py
```

Type `wake`, then ask a short question. The reply should appear in the terminal and play through the speaker. Stop with `Control-C`. `PIE_AGENT_THINKING=auto` keeps ordinary turns fast and enables model thinking for requests such as planning, analysis, calculation, debugging, or “think carefully”; set it to `off` or `on` to override that policy. Set `PIE_AGENT_STREAMING=true` to print model text as it arrives; speech still waits for the completed reply.
