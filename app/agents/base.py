from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    name: str
    status: str = "passed"
    summary: str = ""
    artifacts: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    name = "base_agent"

    def run(self) -> AgentResult:
        return AgentResult(name=self.name, summary="agent stub")
