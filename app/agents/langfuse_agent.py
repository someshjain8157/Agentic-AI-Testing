from __future__ import annotations

from app.agents.base import AgentResult
from app.testing.agents.compliance import LangfuseObservabilityAgent


class LangfuseAgent(LangfuseObservabilityAgent):
    name = "langfuse_agent"

    def run(self) -> AgentResult:
        report = super()._run()
        return AgentResult(
            name=self.name,
            summary=report.summary,
            data={"library": "langfuse", **report.data},
        )
