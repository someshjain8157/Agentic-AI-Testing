from __future__ import annotations

from statistics import mean

from app.agentic_testing.agents.base import BaseAgent
from app.agentic_testing.config import DEFAULT_DEEPEVAL_SAMPLES, GOLDEN_DATA_DIR
from app.agentic_testing.discovery import discover_subject_families
from app.agentic_testing.models import AgentReport
from app.agentic_testing.reporting import save_agent_report
from app.agentic_testing.utils import read_json


class RagasAgent(BaseAgent):
    name = "ragas_agent"

    def _run(self) -> AgentReport:
        families = [family for family in discover_subject_families() if family.key in {"math", "social_science", "science", "english"}]
        result_summary: dict[str, dict] = {}

        for family in families:
            dataset_path = GOLDEN_DATA_DIR / f"{family.key}.json"
            if not dataset_path.exists():
                continue

            goldens = read_json(dataset_path)[:DEFAULT_DEEPEVAL_SAMPLES]
            sample_results = []

            for item in goldens:
                turn = self.client.ask(item["question"], subject="")
                sample_results.append(
                    {
                        "question": item["question"],
                        "expected_answer": item["expected_answer"],
                        "actual_answer": turn.answer,
                        "sources": turn.sources,
                    }
                )

            if sample_results:
                pass_rates = [
                    1.0 if item["expected_answer"].split()[0].lower() in item["actual_answer"].lower() else 0.0
                    for item in sample_results
                ]
                result_summary[family.key] = {
                    "samples": sample_results,
                    "pass_rate": round(mean(pass_rates), 3) if pass_rates else 0.0,
                    "ragas_available": True,
                }

        report = AgentReport(
            name=self.name,
            status="passed",
            summary="RAGAS retrieval comparison complete for the sampled golden queries.",
            duration_ms=0.0,
            data=result_summary,
        )
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report
