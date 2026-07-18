from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.agentic_testing.agents.golden_dataset import GoldenDatasetAgent
from app.agentic_testing.agents.deepeval_agent import DeepEvalAgent
from app.agentic_testing.config import GOLDEN_DATA_DIR


FAMILIES = ("english", "math", "science", "social_science")


@pytest.fixture(scope="module")
def deepeval_report():
    if not all((GOLDEN_DATA_DIR / f"{family}.json").exists() for family in FAMILIES):
        GoldenDatasetAgent().run()
    return DeepEvalAgent().run()


def test_deepeval_quality_gate(deepeval_report):
    assert deepeval_report.status == "passed", (
        f"DeepEval quality gate failed at {deepeval_report.data['overall_pass_rate']:.1%} "
        f"(threshold {deepeval_report.data['threshold']:.1%})"
    )


@pytest.mark.parametrize("family_key", FAMILIES)
def test_deepeval_reports_samples_per_family(deepeval_report, family_key):
    assert family_key in deepeval_report.data["families"]

    family_report = deepeval_report.data["families"][family_key]
    assert family_report["sample_count"] > 0
    assert len(family_report["samples"]) == family_report["sample_count"]
    assert 0.0 <= family_report["pass_rate"] <= 1.0
    assert family_report["status"] in {"passed", "failed"}
    assert family_report["evaluation_engine"] in {"deepeval", "fallback"}
    assert family_report["subject_name"]
    assert all("comparison_score" in sample for sample in family_report["samples"])
    assert all(isinstance(sample["matched_expected"], bool) for sample in family_report["samples"])


def test_deepeval_audit_logs_include_queries_and_answers(deepeval_report):
    audit_path = Path("logs") / "audit.jsonl"
    assert audit_path.exists()

    rows = []
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))

    deepeval_rows = [row for row in rows if row.get("event") == "deepeval.sample_complete"]
    assert deepeval_rows, "Expected deepeval sample audit entries"
    assert all(row.get("question") for row in deepeval_rows)
    assert all(row.get("chatbot_output") for row in deepeval_rows)
    assert all("expected_answer" in row for row in deepeval_rows)
    assert all("comparison_score" in row for row in deepeval_rows)
