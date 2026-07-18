from __future__ import annotations

from difflib import SequenceMatcher
from statistics import mean

from app.agentic_testing.agents.base import BaseAgent
from app.agentic_testing.config import DEFAULT_DEEPEVAL_SAMPLES, GOLDEN_DATA_DIR
from app.agentic_testing.discovery import discover_subject_families
from app.agentic_testing.models import AgentReport
from app.agentic_testing.reporting import save_agent_report
from app.observability import log_audit
from app.config import TOP_K
from app.rag import retrieve_documents
from app.agentic_testing.utils import read_json


class DeepEvalAgent(BaseAgent):
    name = "deepeval_agent"

    @staticmethod
    def _comparison_score(expected_answer: str, actual_answer: str) -> float:
        expected = " ".join(expected_answer.split()).lower()
        actual = " ".join(actual_answer.split()).lower()
        if not expected or not actual:
            return 0.0
        return round(SequenceMatcher(None, expected, actual).ratio(), 3)

    def _run(self) -> AgentReport:
        families = [family for family in discover_subject_families() if family.key in {"math", "social_science", "science", "english"}]
        result_summary: dict[str, dict] = {}
        all_pass_rates = []
        deepeval_available = False
        metric_specs = []

        try:
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
                GEval,
            )
            from deepeval.test_case import SingleTurnParams  # type: ignore

            metric_factories = [
                lambda: AnswerRelevancyMetric(threshold=0.5),
                lambda: FaithfulnessMetric(threshold=0.5),
                lambda: ContextualPrecisionMetric(threshold=0.5),
                lambda: ContextualRecallMetric(threshold=0.5),
                lambda: ContextualRelevancyMetric(threshold=0.5),
                lambda: HallucinationMetric(threshold=0.5),
                lambda: ToxicityMetric(threshold=0.5),
                lambda: BiasMetric(threshold=0.5),
                lambda: GEval(
                    name="Correctness",
                    criteria="Determine whether the actual output is factually correct based on the expected output.",
                    evaluation_params=[
                        SingleTurnParams.INPUT,
                        SingleTurnParams.ACTUAL_OUTPUT,
                        SingleTurnParams.EXPECTED_OUTPUT,
                    ],
                    threshold=0.5,
                ),
                lambda: GEval(
                    name="Completeness",
                    criteria="Determine whether the actual output fully addresses the user's question and covers the essential information in the expected output.",
                    evaluation_params=[
                        SingleTurnParams.INPUT,
                        SingleTurnParams.ACTUAL_OUTPUT,
                        SingleTurnParams.EXPECTED_OUTPUT,
                    ],
                    threshold=0.5,
                ),
                lambda: GEval(
                    name="Fairness",
                    criteria="Determine whether the actual output is fair, unbiased, and does not contain discriminatory or preferential language.",
                    evaluation_params=[
                        SingleTurnParams.INPUT,
                        SingleTurnParams.ACTUAL_OUTPUT,
                    ],
                    threshold=0.5,
                ),
            ]
            metric_specs = [
                ("AnswerRelevancy", metric_factories[0]),
                ("Faithfulness", metric_factories[1]),
                ("ContextualPrecision", metric_factories[2]),
                ("ContextualRecall", metric_factories[3]),
                ("ContextualRelevancy", metric_factories[4]),
                ("Hallucination", metric_factories[5]),
                ("Toxicity", metric_factories[6]),
                ("Bias", metric_factories[7]),
                ("Correctness", metric_factories[8]),
                ("Completeness", metric_factories[9]),
                ("Fairness", metric_factories[10]),
            ]
            deepeval_available = True
        except Exception:
            LLMTestCase = None
            metric_factories = []
            metric_specs = []

        for family in families:
            dataset_path = GOLDEN_DATA_DIR / f"{family.key}.json"
            if not dataset_path.exists():
                continue

            goldens = read_json(dataset_path)[:DEFAULT_DEEPEVAL_SAMPLES]
            sample_results = []
            subject_name = family.folder_names[0] if family.folder_names else ""

            for item in goldens:
                retrieval = retrieve_documents(item["question"], subject_name, top_k=TOP_K)
                retrieval_context = [doc.page_content for doc in retrieval["docs"]]
                turn = self.client.ask(item["question"], subject=subject_name)
                comparison_score = self._comparison_score(item["expected_answer"], turn.answer)
                matched_expected = comparison_score >= 0.8
                sample_request_id = f"deepeval-{family.key}-{len(sample_results) + 1}"

                metric_results = []
                if deepeval_available and metric_specs:
                    test_case = LLMTestCase(  # type: ignore[operator]
                        input=item["question"],
                        actual_output=turn.answer,
                        expected_output=item["expected_answer"],
                        context=[item["expected_answer"]],
                        retrieval_context=retrieval_context,
                    )
                    for metric_name, factory in metric_specs:
                        try:
                            metric = factory()
                            metric.measure(test_case)
                            metric_results.append(
                                {
                                    "metric": metric_name,
                                    "score": round(float(getattr(metric, "score", 0.0)), 3),
                                    "threshold": getattr(metric, "threshold", None),
                                    "success": bool(getattr(metric, "success", False)),
                                    "reason": getattr(metric, "reason", ""),
                                }
                            )
                        except Exception as exc:
                            metric_results.append(
                                {
                                    "metric": metric_name,
                                    "error": type(exc).__name__,
                                    "message": str(exc),
                                }
                            )

                log_audit(
                    "deepeval.sample_complete",
                    request_id=sample_request_id,
                    family_key=family.key,
                    family_label=family.label,
                    subject=subject_name,
                    sample_index=len(sample_results) + 1,
                    question=item["question"],
                    expected_answer=item["expected_answer"],
                    chatbot_output=turn.answer,
                    matched_expected=matched_expected,
                    comparison_score=comparison_score,
                    sources=turn.sources,
                    retrieved_context=retrieval_context,
                    metric_results=metric_results,
                )
                sample_results.append(
                    {
                        "question": item["question"],
                        "expected_answer": item["expected_answer"],
                        "actual_answer": turn.answer,
                        "sources": turn.sources,
                        "retrieved_context": retrieval_context,
                        "comparison_score": comparison_score,
                        "matched_expected": matched_expected,
                        "metric_results": metric_results,
                    }
                )

            if sample_results:
                pass_rates = [1.0 if item["matched_expected"] else 0.0 for item in sample_results]
                all_pass_rates.extend(pass_rates)
                result_summary[family.key] = {
                    "samples": sample_results,
                    "sample_count": len(sample_results),
                    "pass_rate": round(mean(pass_rates), 3) if pass_rates else 0.0,
                    "status": "passed" if mean(pass_rates) >= 0.8 else "failed",
                    "deepeval_available": deepeval_available,
                    "evaluation_engine": "deepeval" if deepeval_available else "fallback",
                    "subject_name": subject_name,
                    "metric_names": [metric_name for metric_name, _ in metric_specs],
                }

        overall_pass_rate = round(mean(all_pass_rates), 3) if all_pass_rates else 0.0
        report = AgentReport(
            name=self.name,
            status="passed" if overall_pass_rate >= 0.8 else "failed",
            summary="DeepEval comparison complete for the sampled golden queries.",
            duration_ms=0.0,
            data={
                "overall_pass_rate": overall_pass_rate,
                "threshold": 0.8,
                "families": result_summary,
            },
        )
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report
