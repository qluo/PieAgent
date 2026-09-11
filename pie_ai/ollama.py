"""Ollama implementation of the provider-neutral model client."""

import json
import os
import time
from collections.abc import Iterator, Sequence

import requests

from .types import (
    ModelEvent,
    ModelMessage,
    ModelResponse,
    ModelUnavailableError,
    ThinkingLevel,
    ToolCall,
    ToolSchema,
)
from .logging import log_event


class OllamaClient:
    """Call a local or LAN-hosted Ollama server through its chat API."""

    def __init__(
        self,
        model_name: str = "qwen3:1.7b",
        base_url: str | None = None,
        timeout: float = 120,
    ) -> None:
        self.model_name = model_name
        self.base_url = (
            base_url
            or os.environ.get("PIE_AGENT_OLLAMA_URL")
            or "http://localhost:11434"
        ).rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        messages: Sequence[ModelMessage],
        tools: Sequence[ToolSchema] = (),
        streaming: bool = False,
        thinking: ThinkingLevel = False,
    ) -> ModelResponse | Iterator[ModelEvent]:
        payload: dict[str, object] = {
            "model": self.model_name,
            "messages": [self._message_payload(message) for message in messages],
            "stream": streaming,
            "think": thinking,
        }
        if tools:
            payload["tools"] = [self._tool_payload(tool) for tool in tools]

        if streaming:
            return self._stream(payload)
        return self._complete(payload)

    def _complete(self, payload: dict[str, object]) -> ModelResponse:
        started_at = time.perf_counter()
        log_event("ai.ollama", "model_request_started", **self._request_fields(payload))
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as error:
            log_event(
                "ai.ollama",
                "model_request_failed",
                level=40,
                duration_ms=round((time.perf_counter() - started_at) * 1000),
                error_type=type(error).__name__,
            )
            raise ModelUnavailableError("Ollama is unavailable.") from error
        log_event(
            "ai.ollama",
            "model_request_finished",
            duration_ms=round((time.perf_counter() - started_at) * 1000),
            http_status=response.status_code,
        )
        return ModelResponse(self._model_message(data.get("message", {})))

    def _stream(self, payload: dict[str, object]) -> Iterator[ModelEvent]:
        started_at = time.perf_counter()
        first_event_at: float | None = None
        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []
        log_event("ai.ollama", "model_request_started", **self._request_fields(payload))
        try:
            with requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
                stream=True,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if first_event_at is None:
                        first_event_at = time.perf_counter()
                        log_event(
                            "ai.ollama",
                            "model_first_event",
                            duration_ms=round((first_event_at - started_at) * 1000),
                        )
                    data = json.loads(line)
                    message = self._model_message(data.get("message", {}))
                    if message.content:
                        text_parts.append(message.content)
                        yield ModelEvent(kind="text_delta", text=message.content)
                    for tool_call in message.tool_calls:
                        tool_calls.append(tool_call)
                        yield ModelEvent(kind="tool_call", tool_call=tool_call)
                    if data.get("done"):
                        yield ModelEvent(
                            kind="completed",
                            message=ModelMessage(
                                role="assistant",
                                content="".join(text_parts),
                                tool_calls=tool_calls.copy(),
                            ),
                        )
        except (requests.RequestException, ValueError) as error:
            log_event(
                "ai.ollama",
                "model_request_failed",
                level=40,
                duration_ms=round((time.perf_counter() - started_at) * 1000),
                error_type=type(error).__name__,
            )
            raise ModelUnavailableError("Ollama is unavailable.") from error
        log_event(
            "ai.ollama",
            "model_request_finished",
            duration_ms=round((time.perf_counter() - started_at) * 1000),
            http_status=response.status_code,
            text_characters=sum(len(part) for part in text_parts),
            tool_call_count=len(tool_calls),
        )

    def _request_fields(self, payload: dict[str, object]) -> dict[str, object]:
        return {
            "model": self.model_name,
            "streaming": bool(payload["stream"]),
            "thinking": payload["think"],
            "message_count": len(payload["messages"]),
            "tool_count": len(payload.get("tools", [])),
        }

    @staticmethod
    def _tool_payload(tool: ToolSchema) -> dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    @staticmethod
    def _message_payload(message: ModelMessage) -> dict[str, object]:
        if message.role == "tool_result":
            return {
                "role": "tool",
                "tool_name": message.tool_name,
                "content": message.content,
            }

        payload: dict[str, object] = {"role": message.role, "content": message.content}
        if message.tool_calls:
            payload["tool_calls"] = [
                {
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments,
                    },
                }
                for call in message.tool_calls
            ]
        return payload

    @staticmethod
    def _model_message(data: dict[str, object]) -> ModelMessage:
        calls = []
        for raw_call in data.get("tool_calls", []) or []:
            function = raw_call.get("function", {})
            calls.append(
                ToolCall(
                    name=str(function.get("name", "")),
                    arguments=dict(function.get("arguments", {}) or {}),
                    call_id=str(function["index"])
                    if function.get("index") is not None
                    else None,
                )
            )
        return ModelMessage(
            role="assistant",
            content=str(data.get("content", "") or ""),
            tool_calls=calls,
        )
