from app.agentic_testing.agents.compliance import BraintrustAuditAgent, GuardrailComplianceAgent, LangfuseObservabilityAgent


class TestComplianceAgents:
    def test_langfuse_agent_runs(self):
        report = LangfuseObservabilityAgent().run()
        assert report.status in {'passed', 'warning'}

    def test_braintrust_agent_runs(self):
        report = BraintrustAuditAgent().run()
        assert report.status in {'passed', 'warning'}

    def test_guardrail_agent_runs(self):
        report = GuardrailComplianceAgent().run()
        assert report.status in {'passed', 'warning'}
