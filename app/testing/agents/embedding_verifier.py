from __future__ import annotations

from statistics import mean

from app.rag import retrieve_documents
from app.testing.agents.base import BaseAgent
from app.testing.config import GOLDEN_DATA_DIR
from app.testing.discovery import discover_subject_families
from app.testing.models import AgentReport
from app.testing.reporting import save_agent_report
from app.testing.utils import read_json


class EmbeddingVerifierAgent(BaseAgent):
    name = "embedding_verifier_agent"

    def _run(self) -> AgentReport:
        families = [family for family in discover_subject_families() if family.key in {"math", "social_science", "science", "english"}]
        subject_scores: dict[str, float] = {}
        details: dict[str, dict] = {}

        for family in families:
            dataset_path = GOLDEN_DATA_DIR / f"{family.key}.json"
            if not dataset_path.exists():
                continue

            goldens = read_json(dataset_path)
            if not goldens:
                continue

            hits = []
            samples = goldens[:2]
            per_sample = []
            for item in samples:
                result = retrieve_documents(item["question"], subject="", top_k=3)
                retrieved_subjects = [doc.metadata.get("subject", "") for doc in result["docs"]]
                hit = any(subject in family.folder_names for subject in retrieved_subjects)
                hits.append(1.0 if hit else 0.0)
                per_sample.append(
                    {
                        "question": item["question"],
                        "retrieved_subjects": retrieved_subjects,
                        "hit": hit,
                    }
                )

            score = mean(hits) if hits else 0.0
            subject_scores[family.key] = round(score, 3)
            details[family.key] = {"samples": per_sample, "score": score}

        report = AgentReport(
            name=self.name,
            status="passed",
            summary="Embedding retrieval verification completed.",
            duration_ms=0.0,
            data={"subject_scores": subject_scores, "details": details, "ragas": {"enabled": False, "note": "Optional adapter can be added if ragas is installed."}},
        )
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report
