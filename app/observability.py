import hashlib
import json
import logging
import os
import re
from datetime import datetime, timezone
from logging import Handler
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from app.config import PROJECT_ROOT

LOG_DIR = PROJECT_ROOT / "logs"
AGENT_LOG_PATH = LOG_DIR / "agent.jsonl"
AUDIT_LOG_PATH = LOG_DIR / "audit.jsonl"

_LOG_LEVEL = os.getenv("TEACHERAI_LOG_LEVEL", "INFO").upper()
_LOG_CONTENT = os.getenv("TEACHERAI_LOG_CONTENT", "0").lower() in {"1", "true", "yes", "on"}

_configured = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_text(text: str, max_length: int = 160) -> str:
    """Return a short, low-risk preview for diagnostics."""

    normalized = " ".join(text.split())
    normalized = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[REDACTED_EMAIL]", normalized)
    normalized = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[REDACTED_PHONE]", normalized)
    if len(normalized) > max_length:
        return normalized[:max_length].rstrip() + "..."
    return normalized


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    return str(value)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }

        data = getattr(record, "data", None)
        if isinstance(data, dict):
            payload.update(data)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=_json_default, ensure_ascii=True)


def _build_handler(handler: Handler) -> Handler:
    handler.setFormatter(JsonFormatter())
    return handler


def configure_logging() -> None:
    global _configured

    if _configured:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    app_logger = logging.getLogger("teacherai")
    app_logger.setLevel(_LOG_LEVEL)
    app_logger.propagate = False
    if not app_logger.handlers:
        console_handler = _build_handler(logging.StreamHandler())
        app_logger.addHandler(console_handler)
        file_handler = _build_handler(
            RotatingFileHandler(
                AGENT_LOG_PATH,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
        )
        app_logger.addHandler(file_handler)

    audit_logger = logging.getLogger("teacherai.audit")
    audit_logger.setLevel(_LOG_LEVEL)
    audit_logger.propagate = False
    if not audit_logger.handlers:
        audit_file_handler = _build_handler(
            RotatingFileHandler(
                AUDIT_LOG_PATH,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
        )
        audit_logger.addHandler(audit_file_handler)

    _configured = True


def get_logger() -> logging.Logger:
    configure_logging()
    return logging.getLogger("teacherai")


def get_audit_logger() -> logging.Logger:
    configure_logging()
    return logging.getLogger("teacherai.audit")


def safe_preview(text: str, max_length: int = 160) -> str:
    return _sanitize_text(text, max_length=max_length)


def audit_payload(
    *,
    request_id: str,
    question: str,
    subject: str,
    request_type: str,
    model: str,
    citations: list[dict[str, Any]] | None = None,
    retrieval_k: int | None = None,
    retrieved_chunks: int | None = None,
    source_count: int | None = None,
    context_chars: int | None = None,
    answer: str | None = None,
    status: str = "success",
    duration_ms: float | None = None,
    retrieval_ms: float | None = None,
    generation_ms: float | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "request_id": request_id,
        "subject": subject,
        "request_type": request_type,
        "model": model,
        "status": status,
        "question_length": len(question),
        "question_hash": hash_text(question),
    }

    if _LOG_CONTENT:
        payload["question"] = question
    else:
        payload["question_preview"] = safe_preview(question)

    if retrieval_k is not None:
        payload["retrieval_k"] = retrieval_k
    if retrieved_chunks is not None:
        payload["retrieved_chunks"] = retrieved_chunks
    if source_count is not None:
        payload["source_count"] = source_count
    if context_chars is not None:
        payload["context_chars"] = context_chars
    if citations is not None:
        payload["citation_count"] = len(citations)
        payload["source_fingerprint"] = hash_text(json.dumps(citations, sort_keys=True, default=_json_default))
        payload["citations"] = citations
    if duration_ms is not None:
        payload["duration_ms"] = round(duration_ms, 2)
    if retrieval_ms is not None:
        payload["retrieval_ms"] = round(retrieval_ms, 2)
    if generation_ms is not None:
        payload["generation_ms"] = round(generation_ms, 2)

    if answer is not None:
        payload["answer_length"] = len(answer)
        payload["answer_hash"] = hash_text(answer)
        if _LOG_CONTENT:
            payload["answer"] = answer
        else:
            payload["answer_preview"] = safe_preview(answer)

    if error is not None:
        payload["error"] = error

    return payload


def log_event(event: str, **data: Any) -> None:
    logger = get_logger()
    logger.info(event, extra={"data": data})


def log_audit(event: str, **data: Any) -> None:
    audit_logger = get_audit_logger()
    audit_logger.info(event, extra={"data": {"timestamp": _utc_now(), "event": event, **data}})
