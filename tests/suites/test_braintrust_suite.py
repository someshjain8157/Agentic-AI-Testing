from __future__ import annotations

from app.agentic_testing.agents.compliance import BraintrustAuditAgent


def test_braintrust_agent_reports_audit_coverage():
    report = BraintrustAuditAgent().run()

    assert report.status == "passed"
    assert report.data["integration"] == "braintrust"
    assert report.data["audit_count"] >= 0
    assert 0.0 <= report.data["coverage"] <= 1.0
