from __future__ import annotations

from app.agentic_testing.agents.compliance import GuardrailComplianceAgent


def test_guardrails_agent_reports_findings():
    report = GuardrailComplianceAgent().run()

    assert report.status in {"passed", "warning"}
    assert report.data["integration"] == "guardrails_ai"
    assert report.data["log_count"] >= 0
    assert isinstance(report.data["findings"], list)
