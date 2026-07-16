from __future__ import annotations

from threading import Lock
from typing import Any


_lock = Lock()
_history: list[dict[str, Any]] = []


def add(role: str, content: str) -> None:
    """Store one chat turn in process memory."""

    with _lock:
        _history.append({"role": role, "content": content})


def get() -> list[dict[str, Any]]:
    """Return a copy of the current conversation history."""

    with _lock:
        return list(_history)


def clear() -> None:
    """Clear the in-memory conversation history."""

    with _lock:
        _history.clear()
