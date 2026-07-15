from __future__ import annotations

from app.agents.base import BaseAgent, AgentResult


class PlaywrightAgent(BaseAgent):
    name = "playwright_agent"

    def run(self) -> AgentResult:
        return AgentResult(
            name=self.name,
            summary="Playwright agent stub",
            data={"library": "playwright"},
        )
