from __future__ import annotations

from app.testing.agents.deepeval_agent import DeepEvalAgent as TestingDeepEvalAgent
from app.agents.base import AgentResult


class DeepEvalAgent(TestingDeepEvalAgent):
    name = "deepeval_agent"

    def run(self) -> AgentResult:
        report = super()._run()
        return AgentResult(
            name=self.name,
            summary=report.summary,
            data={"library": "deepeval", **report.data},
        )
