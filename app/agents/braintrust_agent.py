from __future__ import annotations

from app.agents.base import BaseAgent, AgentResult


class BraintrustAgent(BaseAgent):
    name = "braintrust_agent"

    def run(self) -> AgentResult:
        return AgentResult(
            name=self.name,
            summary="Braintrust agent stub",
            data={"library": "braintrust"},
        )
