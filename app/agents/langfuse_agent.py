from __future__ import annotations

from app.agents.base import BaseAgent, AgentResult


class LangfuseAgent(BaseAgent):
    name = "langfuse_agent"

    def run(self) -> AgentResult:
        return AgentResult(
            name=self.name,
            summary="Langfuse agent stub",
            data={"library": "langfuse"},
        )
