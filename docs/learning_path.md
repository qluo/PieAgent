# Pi Agent Learning Path

## Lesson 1: Demo The Fake Agent

Students run `demo.py` and see the full assistant loop working with fake tools.

## Lesson 2: Build The Face State And Face Controller

Students learn how the agent updates `FaceState`, how the face controller reads it, and how each state maps to PNG pictures in the `faces/` folders copied from the original be-more-agent repo.

## Lesson 3: Add Wake Word Detection

Students replace the fake wake word tool with real wake word detection.

## Lesson 4: Implement The Main Agent Loop

Students move the high-level loop from `demo.py` into `agent/agent.py`.

## Lesson 5: STT, Speech-To-Text

Students replace typed input with microphone-based speech recognition.

## Lesson 6: TTS, Text-To-Speech

Students replace printed responses with spoken audio.

## Lesson 7: LLM

Students use Ollama with a small local open model such as `llama3.2:1b`.

## Lesson 8: Tools, Search

Students use the `duckduckgo_search` package to add a web search tool.

## Lesson 9: Put Everything Together

Students combine the agent loop, face controller, wake word, STT, TTS, local LLM, search, and display into one Raspberry Pi assistant.
