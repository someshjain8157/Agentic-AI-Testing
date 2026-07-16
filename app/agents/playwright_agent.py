from __future__ import annotations

from app.agents.base import AgentResult
from app.testing.agents.playwright_generator import PlaywrightGeneratorAgent


class PlaywrightAgent(PlaywrightGeneratorAgent):
    name = "playwright_agent"

    def run(self) -> AgentResult:
        report = super()._run()
        return AgentResult(
            name=self.name,
            summary=report.summary,
            data={"library": "playwright", **report.data},
        )
