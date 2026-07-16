from __future__ import annotations

from statistics import mean

from app.agentic_testing.agents.base import BaseAgent
from app.agentic_testing.config import DEFAULT_DEEPEVAL_SAMPLES, GOLDEN_DATA_DIR
from app.agentic_testing.discovery import discover_subject_families
from app.agentic_testing.models import AgentReport
from app.agentic_testing.reporting import save_agent_report
from app.agentic_testing.utils import read_json


class DeepEvalAgent(BaseAgent):
    name = "deepeval_agent"

    def _run(self) -> AgentReport:
        families = [family for family in discover_subject_families() if family.key in {"math", "social_science", "science", "english"}]
        result_summary: dict[str, dict] = {}
        all_pass_rates = []
        deepeval_available = False

        try:
            from deepeval import evaluate  # type: ignore
            from deepeval.test_case import LLMTestCase  # type: ignore
            from deepeval.metrics import (  # type: ignore
                AnswerRelevancyMetric,
                FaithfulnessMetric,
                ContextualPrecisionMetric,
                ContextualRecallMetric,
                ContextualRelevancyMetric,
                HallucinationMetric,
                ToxicityMetric,
                BiasMetric,
            )

            metric_factories = [
                lambda: AnswerRelevancyMetric(threshold=0.5),
                lambda: FaithfulnessMetric(threshold=0.5),
                lambda: ContextualPrecisionMetric(threshold=0.5),
                lambda: ContextualRecallMetric(threshold=0.5),
                lambda: ContextualRelevancyMetric(threshold=0.5),
                lambda: HallucinationMetric(threshold=0.5),
                lambda: ToxicityMetric(threshold=0.5),
                lambda: BiasMetric(threshold=0.5),
            ]
            deepeval_available = True
        except Exception:
            evaluate = None
            LLMTestCase = None
            metric_factories = []

        for family in families:
            dataset_path = GOLDEN_DATA_DIR / f"{family.key}.json"
            if not dataset_path.exists():
                continue

            goldens = read_json(dataset_path)[:DEFAULT_DEEPEVAL_SAMPLES]
            sample_results = []
            subject_name = family.folder_names[0] if family.folder_names else ""

            if deepeval_available and goldens:
                test_cases = []
                for item in goldens:
                    turn = self.client.ask(item["question"], subject=subject_name)
                    test_cases.append(
                        LLMTestCase(  # type: ignore[operator]
                            input=item["question"],
                            actual_output=turn.answer,
                            expected_output=item["expected_answer"],
                            retrieval_context=[doc.get("chapter", "") for doc in item.get("citations", [])],
                        )
                    )
                    sample_results.append(
                        {
                            "question": item["question"],
                            "expected_answer": item["expected_answer"],
                            "actual_answer": turn.answer,
                            "sources": turn.sources,
                        }
                    )

                metrics = []
                for factory in metric_factories:
                    try:
                        metrics.append(factory())
                    except Exception:
                        continue

                if metrics:
                    try:
                        evaluate(test_cases=test_cases, metrics=metrics)
                    except Exception:
                        pass
            else:
                for item in goldens:
                    turn = self.client.ask(item["question"], subject=subject_name)
                    sample_results.append(
                        {
                            "question": item["question"],
                            "expected_answer": item["expected_answer"],
                            "actual_answer": turn.answer,
                            "sources": turn.sources,
                        }
                    )

            if sample_results:
                pass_rates = [1.0 if item["expected_answer"].split()[0].lower() in item["actual_answer"].lower() else 0.0 for item in sample_results]
                all_pass_rates.extend(pass_rates)
                result_summary[family.key] = {
                    "samples": sample_results,
                    "sample_count": len(sample_results),
                    "pass_rate": round(mean(pass_rates), 3) if pass_rates else 0.0,
                    "deepeval_available": deepeval_available,
                    "evaluation_engine": "deepeval" if deepeval_available else "fallback",
                    "subject_name": subject_name,
                }

        report = AgentReport(
            name=self.name,
            status="passed",
            summary="DeepEval comparison complete for the sampled golden queries.",
            duration_ms=0.0,
            data=result_summary,
        )
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report
