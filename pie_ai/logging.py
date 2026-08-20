"""Reusable structured logging and trace correlation for AI applications."""

from contextvars import ContextVar, Token
import json
import logging
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4


DATE_DIRECTORY_FORMAT = "%m-%d-%Y"
_LOGGER_NAMESPACE = "pie_agent"
_trace_id: ContextVar[str | None] = ContextVar("pie_trace_id", default=None)
_span_id: ContextVar[str | None] = ContextVar("pie_span_id", default=None)


def begin_trace() -> Token[str | None]:
    """Assign a trace identifier to one logical application run."""
    return _trace_id.set(uuid4().hex)


def end_trace(token: Token[str | None]) -> None:
    """Restore the previous trace context."""
    _trace_id.reset(token)


def begin_span() -> Token[str | None]:
    """Assign a child operation identifier within the active trace."""
    return _span_id.set(uuid4().hex)


def end_span(token: Token[str | None]) -> None:
    """Restore the previous span context."""
    _span_id.reset(token)


def log_event(
    component: str,
    event: str,
    *,
    level: int = logging.INFO,
    **fields: object,
) -> None:
    """Emit metadata-only structured data for one execution step."""
    logging.getLogger(f"{_LOGGER_NAMESPACE}.{component}").log(
        level,
        event,
        extra={
            "pie_event": event,
            "pie_fields": fields,
            "pie_trace_id": _trace_id.get(),
            "pie_span_id": _span_id.get(),
        },
    )


class JsonFormatter(logging.Formatter):
    """Format one structured log record per JSONL line."""

    def __init__(self, logger_namespace: str) -> None:
        super().__init__()
        self.logger_namespace = logger_namespace

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "level": record.levelname,
            "component": record.name.removeprefix(f"{self.logger_namespace}."),
            "event": getattr(record, "pie_event", record.getMessage()),
            "trace_id": getattr(record, "pie_trace_id", None),
            "span_id": getattr(record, "pie_span_id", None),
            "data": getattr(record, "pie_fields", {}),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, separators=(",", ":"))


class DailyJsonlHandler(logging.Handler):
    """Append records to a local-date JSONL file, creating it only on first use."""

    def __init__(self, logs_dir: Path, file_name: str) -> None:
        super().__init__()
        self.logs_dir = logs_dir
        self.file_name = file_name
        self._active_date: date | None = None
        self._stream = None

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._open_for_today()
            assert self._stream is not None
            self._stream.write(self.format(record) + "\n")
            self._stream.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        try:
            if self._stream is not None:
                self._stream.close()
                self._stream = None
        finally:
            super().close()

    def _open_for_today(self) -> None:
        today = datetime.now().astimezone().date()
        if today == self._active_date and self._stream is not None:
            return

        if self._stream is not None:
            self._stream.close()
        log_path = self.logs_dir / today.strftime(DATE_DIRECTORY_FORMAT) / self.file_name
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self._stream = log_path.open("a", encoding="utf-8")
        self._active_date = today


def configure_logging(
    logs_dir: Path,
    *,
    file_name: str = "agent.jsonl",
    logger_namespace: str = "pie_agent",
    level: str = "INFO",
    retention_days: int = 30,
) -> int:
    """Configure generic console and date-partitioned file logging."""
    global _LOGGER_NAMESPACE
    _LOGGER_NAMESPACE = logger_namespace
    removed_directories = remove_expired_log_directories(logs_dir, retention_days)
    logger = logging.getLogger(logger_namespace)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(console_handler)

    file_handler = DailyJsonlHandler(logs_dir, file_name)
    file_handler.setFormatter(JsonFormatter(logger_namespace))
    logger.addHandler(file_handler)
    return removed_directories


def remove_expired_log_directories(logs_dir: Path, retention_days: int) -> int:
    """Delete only date-named log folders outside the requested retention period."""
    if retention_days < 1:
        raise ValueError("retention_days must be at least 1.")
    if not logs_dir.is_dir():
        return 0

    earliest_retained_date = date.today() - timedelta(days=retention_days - 1)
    removed_directories = 0
    for child in logs_dir.iterdir():
        if not child.is_dir():
            continue
        try:
            folder_date = datetime.strptime(child.name, DATE_DIRECTORY_FORMAT).date()
        except ValueError:
            continue
        if folder_date < earliest_retained_date:
            shutil.rmtree(child)
            removed_directories += 1
    return removed_directories
