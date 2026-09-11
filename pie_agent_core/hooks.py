"""Application-neutral extension points around tool execution."""

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import TypeAlias

from .state import AgentState
from .tools import AgentToolResult


class AsyncHookInSyncTurnError(RuntimeError):
    """Raised when a synchronous turn receives an awaitable hook result."""


@dataclass(frozen=True, slots=True)
class ToolCallContext:
    """Read-only details available before a requested tool runs."""

    tool_name: str
    arguments: Mapping[str, object]
    call_id: str | None
    round_number: int
    state: AgentState


@dataclass(frozen=True, slots=True)
class ToolCallDecision:
    """Approve a tool call, optionally replacing its arguments, or reject it."""

    approved: bool = True
    arguments: Mapping[str, object] | None = None
    reason: str | None = None

    @classmethod
    def approve(
        cls, arguments: Mapping[str, object] | None = None
    ) -> "ToolCallDecision":
        return cls(approved=True, arguments=arguments)

    @classmethod
    def reject(cls, reason: str) -> "ToolCallDecision":
        return cls(approved=False, reason=reason)


@dataclass(frozen=True, slots=True)
class ToolExecutionContext:
    """The outcome supplied after an approved, rejected, or failed call."""

    call: ToolCallContext
    arguments: Mapping[str, object]
    result: AgentToolResult
    executed: bool
    exception: Exception | None = None


BeforeToolCall: TypeAlias = Callable[
    [ToolCallContext],
    ToolCallDecision | Awaitable[ToolCallDecision],
]
AfterToolCall: TypeAlias = Callable[
    [ToolExecutionContext],
    AgentToolResult | Awaitable[AgentToolResult],
]
