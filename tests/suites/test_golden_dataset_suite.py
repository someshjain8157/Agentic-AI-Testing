from __future__ import annotations

import pytest

from app.agentic_testing.agents.golden_dataset import GoldenDatasetAgent
from app.agentic_testing.config import ARTIFACT_DIR, DEFAULT_GOLDEN_PER_SUBJECT, GOLDEN_DATA_DIR
from tests._agentic_allure import attach_case, read_json_report


REPORT_PATH = ARTIFACT_DIR / "golden_dataset_agent.json"


def _build_report():
    return GoldenDatasetAgent(output_dir=ARTIFACT_DIR).run()


REPORT = read_json_report(REPORT_PATH, builder=_build_report)


def _cases(report: dict) -> list[dict]:
    cases: list[dict] = []
    subjects = report.get("data", {}).get("subjects", {})
    for subject_key, count in sorted(subjects.items()):
        score = round(min(float(count) / float(DEFAULT_GOLDEN_PER_SUBJECT), 1.0), 3) if DEFAULT_GOLDEN_PER_SUBJECT else 0.0
        passed = int(count) >= DEFAULT_GOLDEN_PER_SUBJECT
        cases.append(
            {
                "id": subject_key,
                "title": f"{subject_key} golden dataset count",
                "subject_key": subject_key,
                "expected_output": f"{DEFAULT_GOLDEN_PER_SUBJECT} examples",
                "actual_output": f"{count} examples",
                "score": score,
                "passed": passed,
                "details": {
                    "generated_file": str(GOLDEN_DATA_DIR / f"{subject_key}.json"),
                },
            }
        )
    return cases


CASES = _cases(REPORT)


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_golden_dataset_case(case):
    attach_case(
        parent_suite="Agentic Evaluation",
        suite="Golden Dataset Agent",
        sub_suite=case["subject_key"],
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
