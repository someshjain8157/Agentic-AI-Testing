from __future__ import annotations

from app.agents.base import BaseAgent, AgentResult


class PyritAgent(BaseAgent):
    name = "pyrit_agent"

    def run(self) -> AgentResult:
        return AgentResult(
            name=self.name,
            summary="PyRIT agent stub",
            data={"library": "pyrit"},
        )
