# Setup

## Create A Virtual Environment With uv

Install `uv` first if you do not already have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate
```

Install the Python packages:

```bash
uv pip install -r requirements.txt
```

Run the fake working Lesson 1 demo:

```bash
uv run python demos/lesson1_demo.py
```

## Run Lesson Tests

Run tests from the project folder, the folder that contains `demos/`, `face/`,
`agent/`, and `pytest.ini`.

Each lesson has its own test folder. Run one small test at a time while you build.
For example, in Lesson 2 you can test `FaceState`, then `FaceRenderer.load()`, then
`FaceRenderer.draw()`:

```bash
uv run pytest tests/lesson_2/test_01_face_state.py
uv run pytest tests/lesson_2/test_03_renderer_load.py
uv run pytest tests/lesson_2/test_04_renderer_draw.py
```

Run a whole lesson folder when you think the lesson is complete:

```bash
uv run pytest tests/lesson_1
uv run pytest tests/lesson_2
uv run pytest tests/lesson_3
uv run pytest tests/lesson_4
uv run pytest tests/lesson_5
uv run pytest tests/lesson_6
uv run pytest tests/lesson_7
uv run pytest tests/lesson_8
uv run pytest tests/lesson_9
```

It is normal for later lesson tests to fail before you implement those lessons.

## Tool Settings

Some skeleton classes have an `__init__()` method that stores settings before
the real implementation is written. For example:

```python
WakeWordTool(model_path="hey_jarvis", threshold=0.5, sample_rate=16000)
SpeechToTextTool(
    seconds=10.0,
    silence_seconds=1.0,
    model_path="models/ggml-base.en.bin",
    whisper_binary="whisper.cpp/build/bin/whisper-cli",
)
TextToSpeechTool(
    voice_model_path="models/piper/en_US-lessac-low.onnx",
    piper_binary="tools/piper/piper",
)
SearchTool(max_results=1, region="us-en")
FaceRenderer(faces_dir="faces")
```

Students can keep the defaults at first, then change one setting at a time
when testing real hardware.

## Raspberry Pi System Packages

On Raspberry Pi OS, install the system tools used by audio, display, and local
build steps. This includes `cmake`, which is required to build `whisper.cpp`:

```bash
sudo apt update
sudo apt install -y \
  git cmake build-essential pkg-config \
  portaudio19-dev alsa-utils \
  python3-dev python3-pip \
  libsdl2-dev
```

Check that the build tools are installed:

```bash
git --version
cmake --version
gcc --version
```

Check that the microphone and speaker are visible:

```bash
arecord -l
aplay -l
```

If your speaker does not play, test it directly. This command keeps running
until you press Ctrl+C:

```bash
speaker-test -t wav -c 2
```

## Ollama Setup

Install Ollama using the official instructions:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

The current code uses `gemma3:1b`:

```bash
ollama pull gemma3:1b
ollama run gemma3:1b
```

Keep Ollama running in the background when the agent starts. The Python code
expects Ollama at:

```text
http://localhost:11434
```

## whisper.cpp Setup For Speech-To-Text

The STT tool listens to the microphone until speech ends, saves a temporary WAV,
and sends that WAV to `whisper.cpp`.

Build `whisper.cpp` from the project folder:

```bash
git clone https://github.com/ggml-org/whisper.cpp.git
cmake -S whisper.cpp -B whisper.cpp/build
cmake --build whisper.cpp/build -j 4
```

Create a model folder and download a small English model:

```bash
mkdir -p models
curl -L \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin \
  -o models/ggml-base.en.bin
```

The default code expects:

```text
whisper.cpp/build/bin/whisper-cli
models/ggml-base.en.bin
```

Test whisper.cpp with any small WAV file:

```bash
whisper.cpp/build/bin/whisper-cli \
  -m models/ggml-base.en.bin \
  -f path/to/test.wav \
  -nt
```

If the Pi feels slow, try `ggml-tiny.en.bin` instead and update
`SpeechToTextTool(model_path=...)`.

## Piper Setup For Text-To-Speech

The voice model files are not the Piper program. Install the Piper binary first.

Check your Raspberry Pi OS architecture:

```bash
uname -m
```

If it prints `aarch64`, use the 64-bit Linux release:

```bash
mkdir -p tools
cd tools
curl -L \
  https://github.com/rhasspy/piper/releases/latest/download/piper_linux_aarch64.tar.gz \
  -o piper.tar.gz
tar -xzf piper.tar.gz
cd ..
```

Test the local Piper binary:

```bash
tools/piper/piper --help
```

If `uname -m` prints `armv7l`, you are using 32-bit Raspberry Pi OS. For this
classroom setup, use 64-bit Raspberry Pi OS so the `aarch64` Piper release works.

Create a voice model folder:

```bash
mkdir -p models/piper
```

Download a Piper voice model and its JSON config into that folder. For example,
using the low-size US English Lessac voice:

```bash
curl -L \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx \
  -o models/piper/en_US-lessac-low.onnx

curl -L \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx.json \
  -o models/piper/en_US-lessac-low.onnx.json
```

The default code expects:

```text
models/piper/en_US-lessac-low.onnx
```

Test Piper and speaker playback:

```bash
echo "Hello from Pi Agent" | \
  tools/piper/piper --model models/piper/en_US-lessac-low.onnx --output-raw | \
  aplay -r 22050 -f S16_LE -t raw -
```

The default Python setting is `piper_binary="tools/piper/piper"`, which matches
the extraction location above. If you install Piper elsewhere, pass its path
when creating `TextToSpeechTool(...)` in `main.py`.

## Display Setup

The face renderer uses `pygame` fullscreen. Run the agent from the Raspberry Pi
desktop session or another session with display access.

If pygame cannot open a display, check:

```bash
echo $DISPLAY
python -m pygame.examples.aliens
```

For a small HDMI display, make sure Raspberry Pi OS can see the screen before
starting the agent.

## Run The Wake Word Audio Demo

Lesson 3 also has a manual microphone demo. This is not a unit test because it
needs real hardware:

```bash
uv run python demos/test_wake_word_audio.py
```

If detection is too hard, try a lower threshold:

```bash
uv run python demos/test_wake_word_audio.py --threshold 0.3
```

## Run The Full Agent On Raspberry Pi

After the Python environment, Ollama, whisper.cpp, Piper, microphone, speaker,
and display are ready, run:

```bash
uv run python main.py
```

Expected flow:

1. The face appears on the display.
2. Say "Hey Jarvis" to wake the agent.
3. Ask a question.
4. The agent listens until you stop speaking.
5. whisper.cpp turns your speech into text.
6. Ollama answers with `gemma3:1b`.
7. Piper speaks the answer through the speaker.
8. The face returns to idle.

If something fails, test one tool at a time:

```bash
uv run python demos/test_wake_word_audio.py
uv run pytest tests/lesson_5
uv run pytest tests/lesson_6
uv run pytest tests/lesson_7
uv run pytest tests/lesson_8
```

## Quick Troubleshooting

Try the smallest check that matches the problem before changing code.

| What you see | First check | Likely next step |
| --- | --- | --- |
| `No module named ...` | `uv pip install -r requirements.txt` | Run the command again with `uv run python ...`, not `python3 ...`. |
| No microphone is listed | `arecord -l` | Reconnect the microphone, then choose the listed device in the wake-word demo with `--device`. |
| No sound from the speaker | `speaker-test -t wav -c 2` | Start at low volume; check the selected Raspberry Pi audio output. Press Ctrl+C to stop the test. |
| Ollama connection error | `ollama run gemma3:1b` | Finish the Ollama install and model download; the agent expects `http://localhost:11434`. |
| `whisper-cli` or a model file is missing | `ls whisper.cpp/build/bin/whisper-cli models/ggml-base.en.bin` | Repeat the whisper.cpp build or model download steps. |
| Piper cannot be found | `tools/piper/piper --help` | Repeat the Piper extraction step, keeping it inside `tools/piper`. |

## Search, Privacy, And Trust

The search lesson sends the words in a search query to an internet search
service. Do not search for names, addresses, school details, passwords, or any
other personal information. Ask a teacher before testing a query you are unsure
about.

Search snippets and AI answers can be wrong, incomplete, or inappropriate.
For an important claim, open and check a trusted source with an adult. Treat
text returned from a search result as information to evaluate, not instructions
that the agent should follow.
