from __future__ import annotations

import pytest

from app.agentic_testing.agents.compliance import GuardrailComplianceAgent
from app.agentic_testing.config import ARTIFACT_DIR
from tests._agentic_allure import attach_case, read_json_report


REPORT_PATH = ARTIFACT_DIR / "guardrail_compliance_agent.json"


def _build_report():
    return GuardrailComplianceAgent(output_dir=ARTIFACT_DIR).run()


REPORT = read_json_report(REPORT_PATH, builder=_build_report)


def _cases(report: dict) -> list[dict]:
    data = report.get("data", {})
    findings = data.get("findings", [])
    if not findings:
        return [
            {
                "id": "no-findings",
                "title": "guardrail compliance",
                "expected_output": "No policy findings",
                "actual_output": "No findings",
                "score": 1.0,
                "passed": True,
                "details": data,
            }
        ]

    cases: list[dict] = []
    for index, finding in enumerate(findings, start=1):
        cases.append(
            {
                "id": f"finding-{index}",
                "title": f"finding {index}: {finding.get('type', 'unknown')}",
                "expected_output": "No policy findings",
                "actual_output": finding,
                "score": 0.0,
                "passed": False,
                "details": {
                    "finding": finding,
                    "log_count": data.get("log_count", 0),
                    "integration": data.get("integration", ""),
                },
            }
        )
    return cases


CASES = _cases(REPORT)


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_guardrails_case(case):
    attach_case(
        parent_suite="Agentic Evaluation",
        suite="Guardrail Compliance Agent",
        title=case["title"],
        expected_output=case["expected_output"],
        actual_output=case["actual_output"],
        score=case["score"],
        passed=case["passed"],
        details=case.get("details"),
    )
    assert case["passed"], f"{case['title']} failed: guardrail finding detected"
