from app.agentic_testing.agents.deepeval_agent import DeepEvalAgent
from app.agentic_testing.models import AgentReport


class TestDeepevalAgentAgent:
    def test_agent_runs(self):
        agent = DeepEvalAgent()
        report = agent.run()
        assert isinstance(report, AgentReport)
        assert report.status in {'passed', 'warning'}
