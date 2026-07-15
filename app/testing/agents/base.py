from __future__ import annotations

import time
from abc import ABC, abstractmethod
from pathlib import Path

from app.testing.client import ChatbotClient
from app.testing.llm import LocalAgentLLM
from app.testing.models import AgentReport
from app.testing.config import DEFAULT_MODEL


class BaseAgent(ABC):
    name: str = "base"

    def __init__(
        self,
        *,
        llm: LocalAgentLLM | None = None,
        client: ChatbotClient | None = None,
        output_dir: Path | None = None,
    ):
        self.llm = llm or LocalAgentLLM(model=DEFAULT_MODEL)
        self.client = client or ChatbotClient()
        self.output_dir = output_dir

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

