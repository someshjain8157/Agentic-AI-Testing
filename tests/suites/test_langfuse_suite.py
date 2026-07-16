from __future__ import annotations

from app.agentic_testing.agents.compliance import LangfuseObservabilityAgent


def test_langfuse_agent_reports_observability_coverage():
    report = LangfuseObservabilityAgent().run()

    assert report.status == "passed"
    assert report.data["integration"] == "langfuse"
    assert report.data["log_count"] >= 0
    assert 0.0 <= report.data["coverage"] <= 1.0
