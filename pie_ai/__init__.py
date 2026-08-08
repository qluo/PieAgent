"""Provider-neutral model contracts and clients."""

from .ollama import OllamaClient
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
]
