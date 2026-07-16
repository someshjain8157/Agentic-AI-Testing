from __future__ import annotations

from app.agents.base import AgentResult
from app.testing.agents.compliance import GuardrailComplianceAgent


class GuardrailsAgent(GuardrailComplianceAgent):
    name = "guardrails_agent"

    def run(self) -> AgentResult:
        report = super()._run()
        return AgentResult(
            name=self.name,
            summary=report.summary,
            data={"library": "guardrails-ai", **report.data},
        )
