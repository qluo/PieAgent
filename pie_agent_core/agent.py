"""The provider- and application-neutral tool-using agent loop."""

from collections.abc import AsyncIterator, Awaitable, Iterator, Sequence
import inspect
import time
from types import MappingProxyType
from typing import TypeVar

from pie_ai import (
    ModelClient,
    ModelEvent,
    ModelMessage,
    ModelResponse,
    ModelUnavailableError,
    ThinkingLevel,
    begin_span,
    begin_trace,
    end_span,
    end_trace,
    log_event,
)

from .context import Context, ConvertToModelMessages, TransformContext
from .conversation import AgentConversation
from .events import AgentEvent
from .hooks import (
    AfterToolCall,
    AsyncHookInSyncTurnError,
    BeforeToolCall,
    ToolCallContext,
    ToolCallDecision,
    ToolExecutionContext,
)
from .messages import AgentMessage, AgentNote
from .state import AgentState
from .tools import AgentTool, AgentToolResult


COMPLEXITY_SIGNALS = (
    "analyze",
    "analyse",
    "calculate",
    "compare",
    "debug",
    "design",
    "explain why",
    "math",
    "plan",
    "reason",
    "solve",
    "step by step",
    "think carefully",
)

HookResult = TypeVar("HookResult")


class Agent:
    """Run a bounded model-and-tool loop for one active conversation."""

    def __init__(
        self,
        model_client: ModelClient,
        tools: Sequence[AgentTool] = (),
        context: Context | None = None,
        conversation: AgentConversation | None = None,
        max_tool_rounds: int = 5,
        thinking_mode: str = "auto",
        state: AgentState | None = None,
        transform_context: TransformContext | None = None,
        convert_to_model_messages: ConvertToModelMessages | None = None,
        before_tool_call: BeforeToolCall | None = None,
        after_tool_call: AfterToolCall | None = None,
    ) -> None:
        if state is not None and conversation is not None:
            raise ValueError("Pass either state or conversation, not both.")
        self.model_client = model_client
        self.tools = {tool.name: tool for tool in tools}
        self.context = context or Context()
        self.transform_context = (
            transform_context or self.context.transform_context
        )
        self.convert_to_model_messages = (
            convert_to_model_messages or self.context.convert_to_model_messages
        )
        self.before_tool_call = before_tool_call
        self.after_tool_call = after_tool_call
        self.state = (
            state
            if state is not None
            else conversation
            if conversation is not None
            else AgentConversation()
        )
        # Keep the original public attribute available to existing callers.
        self.conversation = self.state
        self.max_tool_rounds = max_tool_rounds
        if thinking_mode not in {"auto", "off", "on"}:
            raise ValueError('thinking_mode must be "auto", "off", or "on".')
        self.thinking_mode = thinking_mode
        self._started = False
        self._trace_token = None

    def start(self) -> AgentEvent:
        self._trace_token = begin_trace()
        self._started = True
        log_event("core.agent", "agent_started", tool_count=len(self.tools))
        return AgentEvent(kind="agent_started")

    def finish(self) -> AgentEvent:
        log_event("core.agent", "agent_finished")
        self._started = False
        if self._trace_token is not None:
            end_trace(self._trace_token)
            self._trace_token = None
        return AgentEvent(kind="agent_finished")

    def run_turn(
        self,
        user_text: str,
        notes: Sequence[AgentNote] = (),
        streaming: bool = False,
        thinking: ThinkingLevel | None = None,
    ) -> Iterator[AgentEvent | ModelEvent]:
        """Yield lifecycle events while completing a user request."""
        if not self._started:
            yield self.start()

        span_token = begin_span()
        started_at = time.perf_counter()
        try:
            self.conversation.messages.extend(notes)
            user_message = AgentMessage(kind="user", content=user_text)
            self.conversation.messages.append(user_message)
            log_event(
                "core.agent",
                "turn_started",
                note_count=len(notes),
                conversation_messages=len(self.conversation.messages),
            )
            yield AgentEvent(kind="turn_started", message=user_message)

            notices: list[str] = []
            requested_thinking = (
                self._thinking_for(user_text) if thinking is None else thinking
            )
            try:
                for round_number in range(1, self.max_tool_rounds + 1):
                    response = yield from self._generate(streaming, requested_thinking)
                    assistant = AgentMessage(
                        kind="assistant",
                        content=response.message.content,
                        tool_calls=response.message.tool_calls,
                    )
                    self.conversation.messages.append(assistant)

                    if not assistant.tool_calls:
                        final_message = self._final_message(assistant, notices)
                        log_event(
                            "core.agent",
                            "turn_finished",
                            duration_ms=round(
                                (time.perf_counter() - started_at) * 1000
                            ),
                            status="ok",
                            tool_rounds=round_number - 1,
                        )
                        yield AgentEvent(kind="turn_finished", message=final_message)
                        return

                    for tool_call in assistant.tool_calls:
                        tool_started_at = time.perf_counter()
                        log_event(
                            "core.agent",
                            "tool_started",
                            tool_name=tool_call.name,
                            round=round_number,
                        )
                        yield AgentEvent(kind="tool_started", tool_name=tool_call.name)
                        result = self._execute_tool_with_hooks(
                            tool_call.name,
                            tool_call.arguments,
                            tool_call.call_id,
                            round_number,
                        )
                        if result.user_notice:
                            notices.append(result.user_notice)
                        self.conversation.messages.append(
                            AgentMessage(
                                kind="tool_result",
                                content=result.content,
                                tool_name=tool_call.name,
                            )
                        )
                        log_event(
                            "core.agent",
                            "tool_finished",
                            tool_name=tool_call.name,
                            status=result.status,
                            duration_ms=round(
                                (time.perf_counter() - tool_started_at) * 1000
                            ),
                        )
                        yield AgentEvent(
                            kind="tool_finished",
                            tool_name=tool_call.name,
                            result=result,
                        )

                final_message = AgentMessage(
                    kind="assistant",
                    content=self._with_notices(
                        "I couldn't complete that request after several tool attempts.",
                        notices,
                    ),
                )
                self.conversation.messages.append(final_message)
                log_event(
                    "core.agent",
                    "turn_finished",
                    duration_ms=round((time.perf_counter() - started_at) * 1000),
                    status="tool_limit",
                    tool_rounds=self.max_tool_rounds,
                )
                yield AgentEvent(kind="turn_finished", message=final_message)
            except ModelUnavailableError:
                final_message = AgentMessage(
                    kind="assistant",
                    content=self._with_notices(
                        "I can't reach my language model right now.", notices
                    ),
                )
                self.conversation.messages.append(final_message)
                log_event(
                    "core.agent",
                    "turn_finished",
                    duration_ms=round((time.perf_counter() - started_at) * 1000),
                    status="model_unavailable",
                )
                yield AgentEvent(kind="turn_finished", message=final_message)
        finally:
            end_span(span_token)

    async def run_turn_async(
        self,
        user_text: str,
        notes: Sequence[AgentNote] = (),
        streaming: bool = False,
        thinking: ThinkingLevel | None = None,
    ) -> AsyncIterator[AgentEvent | ModelEvent]:
        """Yield a turn while awaiting hooks on the caller's event loop."""
        if not self._started:
            yield self.start()

        span_token = begin_span()
        started_at = time.perf_counter()
        try:
            self.conversation.messages.extend(notes)
            user_message = AgentMessage(kind="user", content=user_text)
            self.conversation.messages.append(user_message)
            log_event(
                "core.agent",
                "turn_started",
                note_count=len(notes),
                conversation_messages=len(self.conversation.messages),
            )
            yield AgentEvent(kind="turn_started", message=user_message)

            notices: list[str] = []
            requested_thinking = (
                self._thinking_for(user_text) if thinking is None else thinking
            )
            try:
                for round_number in range(1, self.max_tool_rounds + 1):
                    generated = self._request_model(streaming, requested_thinking)
                    if not streaming:
                        assert isinstance(generated, ModelResponse)
                        response = generated
                    else:
                        text_parts: list[str] = []
                        tool_calls = []
                        for event in generated:
                            yield event
                            if event.kind == "text_delta":
                                text_parts.append(event.text)
                            elif (
                                event.kind == "tool_call"
                                and event.tool_call is not None
                            ):
                                tool_calls.append(event.tool_call)
                            elif (
                                event.kind == "completed"
                                and event.message is not None
                            ):
                                if event.message.content and not text_parts:
                                    text_parts.append(event.message.content)
                                if event.message.tool_calls and not tool_calls:
                                    tool_calls.extend(event.message.tool_calls)
                        response = ModelResponse(
                            ModelMessage(
                                role="assistant",
                                content="".join(text_parts),
                                tool_calls=tool_calls,
                            )
                        )

                    assistant = AgentMessage(
                        kind="assistant",
                        content=response.message.content,
                        tool_calls=response.message.tool_calls,
                    )
                    self.conversation.messages.append(assistant)

                    if not assistant.tool_calls:
                        final_message = self._final_message(assistant, notices)
                        log_event(
                            "core.agent",
                            "turn_finished",
                            duration_ms=round(
                                (time.perf_counter() - started_at) * 1000
                            ),
                            status="ok",
                            tool_rounds=round_number - 1,
                        )
                        yield AgentEvent(kind="turn_finished", message=final_message)
                        return

                    for tool_call in assistant.tool_calls:
                        tool_started_at = time.perf_counter()
                        log_event(
                            "core.agent",
                            "tool_started",
                            tool_name=tool_call.name,
                            round=round_number,
                        )
                        yield AgentEvent(kind="tool_started", tool_name=tool_call.name)
                        result = await self._execute_tool_with_hooks_async(
                            tool_call.name,
                            tool_call.arguments,
                            tool_call.call_id,
                            round_number,
                        )
                        if result.user_notice:
                            notices.append(result.user_notice)
                        self.conversation.messages.append(
                            AgentMessage(
                                kind="tool_result",
                                content=result.content,
                                tool_name=tool_call.name,
                            )
                        )
                        log_event(
                            "core.agent",
                            "tool_finished",
                            tool_name=tool_call.name,
                            status=result.status,
                            duration_ms=round(
                                (time.perf_counter() - tool_started_at) * 1000
                            ),
                        )
                        yield AgentEvent(
                            kind="tool_finished",
                            tool_name=tool_call.name,
                            result=result,
                        )

                final_message = AgentMessage(
                    kind="assistant",
                    content=self._with_notices(
                        "I couldn't complete that request after several tool attempts.",
                        notices,
                    ),
                )
                self.conversation.messages.append(final_message)
                log_event(
                    "core.agent",
                    "turn_finished",
                    duration_ms=round((time.perf_counter() - started_at) * 1000),
                    status="tool_limit",
                    tool_rounds=self.max_tool_rounds,
                )
                yield AgentEvent(kind="turn_finished", message=final_message)
            except ModelUnavailableError:
                final_message = AgentMessage(
                    kind="assistant",
                    content=self._with_notices(
                        "I can't reach my language model right now.", notices
                    ),
                )
                self.conversation.messages.append(final_message)
                log_event(
                    "core.agent",
                    "turn_finished",
                    duration_ms=round((time.perf_counter() - started_at) * 1000),
                    status="model_unavailable",
                )
                yield AgentEvent(kind="turn_finished", message=final_message)
        finally:
            end_span(span_token)

    def _request_model(
        self, streaming: bool, thinking: ThinkingLevel
    ) -> ModelResponse | Iterator[ModelEvent]:
        prepared = self.transform_context(
            self.conversation.messages, self.conversation
        )
        model_messages = self.convert_to_model_messages(prepared)
        log_event(
            "core.context",
            "context_prepared",
            conversation_messages=len(self.conversation.messages),
            prepared_messages=len(prepared),
            model_messages=len(model_messages),
            streaming=streaming,
            thinking=thinking,
        )
        return self.model_client.generate(
            model_messages,
            list(self.tools.values()),
            streaming=streaming,
            thinking=thinking,
        )

    def _generate(
        self, streaming: bool, thinking: ThinkingLevel
    ) -> Iterator[ModelEvent]:
        generated = self._request_model(streaming, thinking)
        if not streaming:
            assert isinstance(generated, ModelResponse)
            return generated

        text_parts: list[str] = []
        tool_calls = []
        for event in generated:
            yield event
            if event.kind == "text_delta":
                text_parts.append(event.text)
            elif event.kind == "tool_call" and event.tool_call is not None:
                tool_calls.append(event.tool_call)
            elif event.kind == "completed" and event.message is not None:
                if event.message.content and not text_parts:
                    text_parts.append(event.message.content)
                if event.message.tool_calls and not tool_calls:
                    tool_calls.extend(event.message.tool_calls)
        return ModelResponse(
            ModelMessage(
                role="assistant",
                content="".join(text_parts),
                tool_calls=tool_calls,
            )
        )

    def _execute_tool(
        self, name: str, arguments: dict[str, object]
    ) -> AgentToolResult:
        tool = self.tools.get(name)
        if tool is None:
            return AgentToolResult(
                f"The requested tool '{name}' is unavailable.", "error"
            )
        try:
            return tool.execute(arguments)
        except Exception as error:
            return AgentToolResult(f"Tool '{name}' failed: {error}", "error")

    def _execute_tool_with_hooks(
        self,
        name: str,
        arguments: dict[str, object],
        call_id: str | None,
        round_number: int,
    ) -> AgentToolResult:
        """Run both hook boundaries and the tool to completion, in order."""
        if self.before_tool_call is None and self.after_tool_call is None:
            return self._execute_tool(name, arguments)

        original_arguments, call = self._tool_call_context(
            name, arguments, call_id, round_number
        )
        decision = ToolCallDecision.approve()
        hook_error: Exception | None = None

        if self.before_tool_call is not None:
            try:
                decision = self._resolve_sync_hook(
                    self.before_tool_call(call), "before_tool_call"
                )
                self._require_decision(decision)
            except AsyncHookInSyncTurnError:
                raise
            except Exception as error:
                hook_error = error
                decision = ToolCallDecision.reject(
                    f"Before-tool hook failed for '{name}': {error}"
                )

        outcome = self._execute_decision(
            call, original_arguments, decision, hook_error
        )
        if self.after_tool_call is None:
            return outcome.result

        try:
            final_result = self._resolve_sync_hook(
                self.after_tool_call(outcome), "after_tool_call"
            )
            self._require_tool_result(final_result, "after_tool_call")
            return final_result
        except AsyncHookInSyncTurnError:
            raise
        except Exception as error:
            return self._post_hook_failure(name, error)

    async def _execute_tool_with_hooks_async(
        self,
        name: str,
        arguments: dict[str, object],
        call_id: str | None,
        round_number: int,
    ) -> AgentToolResult:
        """Run hooks on the caller's event loop, one tool call at a time."""
        if self.before_tool_call is None and self.after_tool_call is None:
            return self._execute_tool(name, arguments)

        original_arguments, call = self._tool_call_context(
            name, arguments, call_id, round_number
        )
        decision = ToolCallDecision.approve()
        hook_error: Exception | None = None

        if self.before_tool_call is not None:
            try:
                decision = await self._resolve_async_hook(self.before_tool_call(call))
                self._require_decision(decision)
            except Exception as error:
                hook_error = error
                decision = ToolCallDecision.reject(
                    f"Before-tool hook failed for '{name}': {error}"
                )

        outcome = self._execute_decision(
            call, original_arguments, decision, hook_error
        )
        if self.after_tool_call is None:
            return outcome.result

        try:
            final_result = await self._resolve_async_hook(self.after_tool_call(outcome))
            self._require_tool_result(final_result, "after_tool_call")
            return final_result
        except Exception as error:
            return self._post_hook_failure(name, error)

    def _tool_call_context(
        self,
        name: str,
        arguments: dict[str, object],
        call_id: str | None,
        round_number: int,
    ) -> tuple[dict[str, object], ToolCallContext]:
        original_arguments = dict(arguments)
        return original_arguments, ToolCallContext(
            tool_name=name,
            arguments=MappingProxyType(original_arguments),
            call_id=call_id,
            round_number=round_number,
            state=self.state,
        )

    def _execute_decision(
        self,
        call: ToolCallContext,
        original_arguments: dict[str, object],
        decision: ToolCallDecision,
        hook_error: Exception | None,
    ) -> ToolExecutionContext:
        effective_arguments = dict(
            original_arguments if decision.arguments is None else decision.arguments
        )
        executed = False
        execution_error = hook_error

        if not decision.approved:
            result = AgentToolResult(
                decision.reason or f"Tool '{call.tool_name}' was declined.",
                "error" if hook_error is not None else "declined",
            )
        else:
            tool = self.tools.get(call.tool_name)
            if tool is None:
                execution_error = LookupError(f"Unknown tool: {call.tool_name}")
                result = AgentToolResult(
                    f"The requested tool '{call.tool_name}' is unavailable.", "error"
                )
            else:
                executed = True
                try:
                    result = tool.execute(effective_arguments)
                    self._require_tool_result(result, "AgentTool.execute")
                except Exception as error:
                    execution_error = error
                    result = AgentToolResult(
                        f"Tool '{call.tool_name}' failed: {error}", "error"
                    )

        return ToolExecutionContext(
            call=call,
            arguments=MappingProxyType(effective_arguments),
            result=result,
            executed=executed,
            exception=execution_error,
        )

    @staticmethod
    def _resolve_sync_hook(
        value: HookResult | Awaitable[HookResult],
        hook_name: str,
    ) -> HookResult:
        """Return a synchronous hook result or direct callers to the async API."""
        if not inspect.isawaitable(value):
            return value
        if inspect.iscoroutine(value):
            value.close()
        raise AsyncHookInSyncTurnError(
            f"{hook_name} returned an awaitable; use Agent.run_turn_async() "
            "for asynchronous hooks."
        )

    @staticmethod
    async def _resolve_async_hook(
        value: HookResult | Awaitable[HookResult],
    ) -> HookResult:
        if inspect.isawaitable(value):
            return await value
        return value

    @staticmethod
    def _require_decision(value: object) -> None:
        if not isinstance(value, ToolCallDecision):
            raise TypeError("before_tool_call must return ToolCallDecision")

    @staticmethod
    def _require_tool_result(value: object, source: str) -> None:
        if not isinstance(value, AgentToolResult):
            raise TypeError(f"{source} must return AgentToolResult")

    @staticmethod
    def _post_hook_failure(name: str, error: Exception) -> AgentToolResult:
        # Do not expose an unprocessed result when a redaction or policy hook fails.
        return AgentToolResult(
            f"After-tool hook failed for '{name}': {error}", "error"
        )

    def _thinking_for(self, user_text: str) -> bool:
        """Keep routine turns fast; reason only for explicit complex work."""
        if self.thinking_mode == "on":
            return True
        if self.thinking_mode == "off":
            return False
        normalized = user_text.lower()
        return any(signal in normalized for signal in COMPLEXITY_SIGNALS)

    def _final_message(
        self, assistant: AgentMessage, notices: Sequence[str]
    ) -> AgentMessage:
        assistant.content = self._with_notices(assistant.content, notices)
        return assistant

    @staticmethod
    def _with_notices(text: str, notices: Sequence[str]) -> str:
        unique_notices = list(dict.fromkeys(notice for notice in notices if notice))
        if not unique_notices:
            return text
        return f"{text}\n\n" + "\n".join(unique_notices)
