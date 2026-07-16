from __future__ import annotations

from app.agents.base import AgentResult
from app.testing.agents.pyrit_attack import PyRITAttackAgent


class PyritAgent(PyRITAttackAgent):
    name = "pyrit_agent"

    def run(self) -> AgentResult:
        report = super()._run()
        return AgentResult(
            name=self.name,
            summary=report.summary,
            data={"library": "pyrit", **report.data},
        )
