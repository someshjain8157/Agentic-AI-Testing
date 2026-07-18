from __future__ import annotations

import pytest

from app.agentic_testing.agents.compliance import BraintrustAuditAgent
from app.agentic_testing.config import ARTIFACT_DIR
from tests._agentic_allure import attach_case, read_json_report


REPORT_PATH = ARTIFACT_DIR / "braintrust_audit_agent.json"


def _build_report():
    return BraintrustAuditAgent(output_dir=ARTIFACT_DIR).run()


REPORT = read_json_report(REPORT_PATH, builder=_build_report)


CASES = [
    {
        "id": "audit-coverage",
        "title": "audit log coverage",
        "expected_output": "Coverage at or above 0.8 with question, answer, citations, and request IDs present",
        "actual_output": {
            "integration": REPORT.get("data", {}).get("integration", ""),
            "coverage": REPORT.get("data", {}).get("coverage", 0.0),
            "audit_count": REPORT.get("data", {}).get("audit_count", 0),
        },
        "score": float(REPORT.get("data", {}).get("coverage", 0.0)),
        "passed": float(REPORT.get("data", {}).get("coverage", 0.0)) >= 0.8,
        "details": REPORT.get("data", {}),
    }
]


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_braintrust_case(case):
    attach_case(
        parent_suite="Agentic Evaluation",
        suite="Braintrust Audit Agent",
        title=case["title"],
        expected_output=case["expected_output"],
        actual_output=case["actual_output"],
        score=case["score"],
        passed=case["passed"],
        details=case.get("details"),
    )
    assert case["passed"], (
        f"{case['title']} failed: coverage {case['score']:.3f} is below the threshold"
    )
