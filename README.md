# Pie Agent

Pie Agent is a small Raspberry Pi voice assistant project for students. You will
build it one lesson at a time: face display, wake word, speech-to-text,
text-to-speech, local LLM, search, and final wiring.

## Start Here

1. Open the full lesson guide:
   - `docs/self_guided_teaching_materials.html`
2. Follow the setup guide:
   - `docs/setup.md`
3. Run Lesson 1 first:

```bash
uv run python demos/lesson1_demo.py
```

Lesson 1 is already working. Later lessons contain TODOs for you to implement.

## Project Map

- `demos/`: checkpoint demos for Lessons 1 through 8.
- `face/`: face state, renderer, and display controller.
- `faces/`: PNG face images for each agent state.
- `agent/`: main agent loop.
- `agent/tools/`: wake word, STT, TTS, LLM, and search tools.
- `tests/`: lesson-by-lesson tests.
- `docs/`: setup guide, architecture notes, and teaching materials.

## Setup

Create a virtual environment and install Python packages:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

If you do not have `uv`, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Raspberry Pi, also follow `docs/setup.md` for system packages, microphone,
speaker, Ollama, whisper.cpp, and Piper.

## How To Work

Run one lesson test at a time while you build:

```bash
uv run pytest tests/lesson_2
```

It is normal for later lesson tests to fail before you reach those lessons.

Good workflow:

1. Read the lesson in `docs/self_guided_teaching_materials.html`.
2. Open the Python file named in the lesson.
3. Implement one TODO.
4. Run the matching test.
5. Repeat.

## Final Goal

When all lessons are complete, Pie Agent should:

1. show animated face states,
2. wake up from voice,
3. listen to a spoken question,
4. transcribe speech with whisper.cpp,
5. answer with Ollama using `gemma3:1b`,
6. use search when helpful,
7. speak the answer with Piper.

Start small, test often, and make one part work before moving to the next.
