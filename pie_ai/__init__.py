"""Provider-neutral model contracts and clients."""

from .ollama import OllamaClient
from .logging import (
    begin_span,
    begin_trace,
    configure_logging,
    end_span,
    end_trace,
    log_event,
)
from .types import (
    ModelClient,
    ModelEvent,
    ModelMessage,
    ModelResponse,
    ModelUnavailableError,
    ThinkingLevel,
    ToolCall,
    ToolSchema,
)

__all__ = [
    "ModelClient",
    "ModelEvent",
    "ModelMessage",
    "ModelResponse",
    "ModelUnavailableError",
    "OllamaClient",
    "ToolCall",
    "ToolSchema",
    "ThinkingLevel",
    "begin_span",
    "begin_trace",
    "configure_logging",
    "end_span",
    "end_trace",
    "log_event",
]
