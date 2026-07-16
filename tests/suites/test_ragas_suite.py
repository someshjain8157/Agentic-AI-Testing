from __future__ import annotations

import pytest

from app.agentic_testing.agents.golden_dataset import GoldenDatasetAgent
from app.agentic_testing.agents.ragas_agent import RagasAgent
from app.agentic_testing.config import GOLDEN_DATA_DIR


FAMILIES = ("english", "math", "science", "social_science")


@pytest.fixture(scope="module")
def ragas_report():
    if not all((GOLDEN_DATA_DIR / f"{family}.json").exists() for family in FAMILIES):
        GoldenDatasetAgent().run()
    return RagasAgent().run()


@pytest.mark.parametrize("family_key", FAMILIES)
def test_ragas_reports_samples_per_family(ragas_report, family_key):
    assert ragas_report.status == "passed"
    assert family_key in ragas_report.data

    family_report = ragas_report.data[family_key]
    assert family_report["sample_count"] > 0
    assert len(family_report["samples"]) == family_report["sample_count"]
    assert 0.0 <= family_report["pass_rate"] <= 1.0
    assert family_report["ragas_available"] is True
    assert family_report["subject_name"]
