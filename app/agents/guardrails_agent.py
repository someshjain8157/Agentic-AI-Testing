from __future__ import annotations

from app.agents.base import BaseAgent, AgentResult


class GuardrailsAgent(BaseAgent):
    name = "guardrails_agent"

    def run(self) -> AgentResult:
        return AgentResult(
            name=self.name,
            summary="Guardrails agent stub",
            data={"library": "guardrails-ai"},
        )
