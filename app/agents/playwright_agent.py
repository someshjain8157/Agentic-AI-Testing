from __future__ import annotations

from app.agents.base import BaseAgent, AgentResult


class PlaywrightAgent(BaseAgent):
    name = "playwright_agent"

    def run(self) -> AgentResult:
        embedded_agents = [
            {"name": "deepeval_agent", "type": "quality"},
            {"name": "ragas_agent", "type": "retrieval"},
            {"name": "pyrit_agent", "type": "adversarial"},
            {"name": "langfuse_agent", "type": "observability"},
            {"name": "braintrust_agent", "type": "experiment"},
            {"name": "guardrails_agent", "type": "safety"},
        ]

        return AgentResult(
            name=self.name,
            summary="Playwright browser workflow includes the other agent-related checks",
            data={
                "library": "playwright",
                "agent_count": len(embedded_agents),
                "embedded_agents": embedded_agents,
            },
        )
