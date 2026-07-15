from __future__ import annotations

from app.agents.base import BaseAgent, AgentResult


class RagasAgent(BaseAgent):
    name = "ragas_agent"

    def run(self) -> AgentResult:
        return AgentResult(
            name=self.name,
            summary="RAGAS agent stub",
            data={"library": "ragas"},
        )
