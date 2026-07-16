from __future__ import annotations

from app.agentic_testing.agents.pyrit_attack import PyRITAttackAgent
from app.agentic_testing.config import DEFAULT_PYRIT_QUERIES


def test_pyrit_agent_runs_real_attacks():
    report = PyRITAttackAgent().run()

    assert report.status in {"passed", "warning"}
    assert report.data["total"] == DEFAULT_PYRIT_QUERIES
    assert len(report.data["results"]) == DEFAULT_PYRIT_QUERIES
    assert report.data["blocked_count"] <= report.data["total"]
    assert all("prompt" in item and "answer" in item for item in report.data["results"])
