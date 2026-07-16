from app.agentic_testing.agents.ragas_agent import RagasAgent
from app.agentic_testing.models import AgentReport


class TestRagasAgentAgent:
    def test_agent_runs(self):
        agent = RagasAgent()
        report = agent.run()
        assert isinstance(report, AgentReport)
        assert report.status in {'passed', 'warning'}
