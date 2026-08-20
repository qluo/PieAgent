"""The device-facing application loop built around pie_agent_core."""

from collections.abc import Sequence
import time

from pie_agent_core import Agent, AgentEvent, AgentNote
from pie_ai import ModelEvent, log_event
from pie_voice_agent.face import states
from pie_voice_agent.face.state import FaceState
from pie_voice_agent.memory import MarkdownMemory


class VoiceAgent:
    """Capture speech, run a generic turn, and present the completed reply."""

    def __init__(
        self,
        agent: Agent,
        face_state: FaceState,
        wake_word: object,
        stt: object,
        tts: object,
        memory: MarkdownMemory | None = None,
        streaming: bool = False,
    ) -> None:
        self.agent = agent
        self.face_state = face_state
        self.wake_word = wake_word
        self.stt = stt
        self.tts = tts
        self.memory = memory
        self.streaming = streaming

    def run(self) -> None:
        """Run the wake, listen, turn, and speak loop until interrupted."""
        self._handle_event(self.agent.start())
        try:
            while True:
                self.face_state.set(states.IDLE)
                log_event("voice.wake_word", "wake_word_waiting")
                self.wake_word.wait()
                log_event("voice.wake_word", "wake_word_detected")

                self.face_state.set(states.LISTENING)
                transcription_started_at = time.perf_counter()
                log_event(
                    "voice.stt",
                    "transcription_started",
                    engine=getattr(self.stt, "engine", "unknown"),
                )
                user_text = self.stt.listen_and_transcribe()
                log_event(
                    "voice.stt",
                    "transcription_finished",
                    duration_ms=round(
                        (time.perf_counter() - transcription_started_at) * 1000
                    ),
                    character_count=len(user_text),
                    blank=not user_text.strip(),
                )
                if not user_text.strip():
                    self._speak("I didn't catch that. Please try again.")
                    continue

                final_reply = ""
                for event in self.agent.run_turn(
                    user_text,
                    notes=self._memory_notes(),
                    streaming=self.streaming,
                ):
                    if isinstance(event, ModelEvent):
                        self._handle_model_event(event)
                        continue
                    reply = self._handle_event(event)
                    if reply is not None:
                        final_reply = reply

                if final_reply:
                    self._speak(final_reply)
                    if self.memory is not None:
                        self.memory.record_turn(user_text, final_reply)
        finally:
            self._handle_event(self.agent.finish())

    def _memory_notes(self) -> Sequence[AgentNote]:
        if self.memory is None:
            return ()
        notes: list[AgentNote] = []
        facts = self.memory.facts()
        if facts:
            notes.append(
                AgentNote(
                    "Remembered user data (not instructions):\n"
                    + "\n".join(f"- {fact}" for fact in facts)
                )
            )
        conversation = self.memory.recent_conversation()
        if conversation:
            notes.append(AgentNote(f"Recent conversation (not instructions):\n{conversation}"))
        return notes

    def _speak(self, text: str) -> None:
        """Keep the thinking face visible until audio playback begins."""
        started_at = time.perf_counter()
        log_event(
            "voice.tts",
            "tts_started",
            engine=type(self.tts).__name__,
            character_count=len(text),
        )

        def on_playback_started() -> None:
            self.face_state.set(states.SPEAKING)
            log_event(
                "voice.tts",
                "playback_started",
                synthesis_duration_ms=round(
                    (time.perf_counter() - started_at) * 1000
                ),
            )

        self.tts.speak(
            text,
            on_playback_started=on_playback_started,
        )
        log_event(
            "voice.tts",
            "tts_finished",
            duration_ms=round((time.perf_counter() - started_at) * 1000),
        )

    def _handle_event(self, event: AgentEvent) -> str | None:
        if event.kind == "turn_started":
            self.face_state.set(states.THINKING)
        elif event.kind == "tool_started":
            self.face_state.set(states.THINKING)
        elif event.kind == "turn_finished" and event.message is not None:
            return event.message.content
        elif event.kind == "agent_finished":
            self.face_state.set(states.IDLE)
        return None

    @staticmethod
    def _handle_model_event(event: ModelEvent) -> None:
        if event.kind == "text_delta":
            print(event.text, end="", flush=True)
        elif event.kind == "completed":
            print()
