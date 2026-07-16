from __future__ import annotations

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from app.agentic_testing.models import AgentReport
from app.agentic_testing.config import DEFAULT_MODEL

if TYPE_CHECKING:
    from app.agentic_testing.client import ChatbotClient
    from app.agentic_testing.llm import LocalAgentLLM


class BaseAgent(ABC):
    name: str = "base"

    def __init__(
        self,
        *,
        llm: "LocalAgentLLM | None" = None,
        client: "ChatbotClient | None" = None,
        output_dir: Path | None = None,
    ):
        self._llm = llm
        self._client = client
        self.output_dir = output_dir

    @property
    def llm(self) -> "LocalAgentLLM":
        if self._llm is None:
            from app.agentic_testing.llm import LocalAgentLLM

            self._llm = LocalAgentLLM(model=DEFAULT_MODEL)
        return self._llm

    @property
    def client(self) -> "ChatbotClient":
        if self._client is None:
            from app.agentic_testing.client import ChatbotClient

            self._client = ChatbotClient()
        return self._client

    def run(self) -> AgentReport:
        started = time.perf_counter()
        try:
            report = self._run()
            report.duration_ms = round((time.perf_counter() - started) * 1000, 2)
            return report
        except Exception as exc:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            return AgentReport(
                name=self.name,
                status="failed",
                summary=f"{self.name} failed: {type(exc).__name__}: {exc}",
                duration_ms=duration_ms,
                data={"error": type(exc).__name__, "message": str(exc)},
            )

    @abstractmethod
    def _run(self) -> AgentReport:
        raise NotImplementedError

