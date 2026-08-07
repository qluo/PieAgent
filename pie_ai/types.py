"""Small, provider-neutral LLM data contracts."""

from dataclasses import dataclass, field
from typing import Iterator, Literal, Protocol, Sequence


MessageRole = Literal["system", "user", "assistant", "tool_result"]
EventKind = Literal["text_delta", "tool_call", "completed"]


class ModelUnavailableError(RuntimeError):
    """Raised when a configured language-model provider cannot respond."""


@dataclass(slots=True)
class ToolSchema:
    """Declarative description of a tool a model may request."""

    name: str
    description: str
    parameters: dict[str, object]


@dataclass(slots=True)
class ToolCall:
    """A model request to execute one declarative tool."""

    name: str
    arguments: dict[str, object]
    call_id: str | None = None


@dataclass(slots=True)
class ModelMessage:
    """A provider-neutral message visible to the language model."""

    role: MessageRole
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_name: str | None = None


@dataclass(slots=True)
class ModelResponse:
    """A completed model response."""

    message: ModelMessage


@dataclass(slots=True)
class ModelEvent:
    """A normalized streamed model chunk."""

    kind: EventKind
    text: str = ""
    tool_call: ToolCall | None = None
    message: ModelMessage | None = None


class ModelClient(Protocol):
    """A client that completes or streams one model request."""

    def generate(
        self,
        messages: Sequence[ModelMessage],
        tools: Sequence[ToolSchema] = (),
        streaming: bool = False,
    ) -> ModelResponse | Iterator[ModelEvent]: ...
