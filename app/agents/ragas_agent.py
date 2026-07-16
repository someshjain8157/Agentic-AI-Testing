from __future__ import annotations

from app.agents.base import AgentResult
from app.testing.agents.embedding_verifier import EmbeddingVerifierAgent


class RagasAgent(EmbeddingVerifierAgent):
    name = "ragas_agent"

    def run(self) -> AgentResult:
        report = super()._run()
        return AgentResult(
            name=self.name,
            summary=report.summary,
            data={"library": "ragas", **report.data},
        )
