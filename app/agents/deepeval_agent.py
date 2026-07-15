from __future__ import annotations

from app.agents.base import BaseAgent, AgentResult


class DeepEvalAgent(BaseAgent):
    name = "deepeval_agent"

    def run(self) -> AgentResult:
        return AgentResult(
            name=self.name,
            summary="DeepEval agent stub",
            data={"library": "deepeval"},
        )
