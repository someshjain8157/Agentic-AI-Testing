from __future__ import annotations

import pytest

from app.agentic_testing.agents.golden_dataset import GoldenDatasetAgent
from app.agentic_testing.agents.ragas_agent import RagasAgent
from app.agentic_testing.config import ARTIFACT_DIR, GOLDEN_DATA_DIR
from tests._agentic_allure import attach_case, read_json_report


FAMILIES = ("english", "math", "science", "social_science")
REPORT_PATH = ARTIFACT_DIR / "ragas_agent.json"


def _build_report():
    if not all((GOLDEN_DATA_DIR / f"{family}.json").exists() for family in FAMILIES):
        GoldenDatasetAgent(output_dir=ARTIFACT_DIR).run()
    return RagasAgent(output_dir=ARTIFACT_DIR).run()


REPORT = read_json_report(REPORT_PATH, builder=_build_report)


def _binary_score(expected_output: str, actual_output: str) -> float:
    expected_first_word = expected_output.split()[0].lower() if expected_output.split() else ""
    return 1.0 if expected_first_word and expected_first_word in actual_output.lower() else 0.0


def _cases(report: dict) -> list[dict]:
    cases: list[dict] = []
    families = report.get("data", {})
    for family_key, family_report in sorted(families.items()):
        samples = family_report.get("samples", [])
        for index, sample in enumerate(samples, start=1):
            expected_output = sample.get("expected_output") or sample.get("expected_answer", "")
            actual_output = sample.get("actual_output") or sample.get("actual_answer", "")
            score = _binary_score(expected_output, actual_output)
            passed = score >= 0.5
            cases.append(
                {
                    "id": f"{family_key}-{index}",
                    "family_key": family_key,
                    "title": f"{family_key} sample {index}: {sample.get('question', '')}",
                    "expected_output": expected_output,
                    "actual_output": actual_output,
                    "score": score,
                    "passed": passed,
                    "details": {
                        "question": sample.get("question", ""),
                        "sources": sample.get("sources", []),
                        "sample_index": index,
                        "pass_rate": family_report.get("pass_rate"),
                        "ragas_available": family_report.get("ragas_available"),
                    },
                }
            )
    return cases


CASES = _cases(REPORT)


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_ragas_case(case):
    attach_case(
        parent_suite="Agentic Evaluation",
        suite="RAGAS Agent",
        sub_suite=case["family_key"],
        title=case["title"],
        expected_output=case["expected_output"],
        actual_output=case["actual_output"],
        score=case["score"],
        passed=case["passed"],
        details=case.get("details"),
    )
    assert case["passed"], (
        f"{case['title']} failed: expected {case['expected_output']} but got {case['actual_output']} "
        f"(score={case['score']:.3f})"
    )
