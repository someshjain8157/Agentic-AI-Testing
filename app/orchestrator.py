from __future__ import annotations

from pathlib import Path
from typing import Any

from app.agents.base import AgentResult
from app.agents.deepeval_agent import DeepEvalAgent
from app.agents.playwright_agent import PlaywrightAgent
from app.agents.pyrit_agent import PyritAgent
from app.agents.ragas_agent import RagasAgent


class AgentOrchestrator:
    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("reports/allure")
        self.agents = [
            DeepEvalAgent(),
            RagasAgent(),
            PyritAgent(),
            PlaywrightAgent(),
        ]

    def run(self) -> list[AgentResult]:
        results: list[AgentResult] = []
        for agent in self.agents:
            result = agent.run()
            results.append(result)
        return results


def main() -> int:
    orchestrator = AgentOrchestrator()
    results = orchestrator.run()
    for result in results:
        print(f"{result.name}: {result.status} - {result.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
