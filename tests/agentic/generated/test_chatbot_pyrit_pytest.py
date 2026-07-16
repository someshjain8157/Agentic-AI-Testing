from app.agentic_testing.agents.pyrit_attack import PyRITAttackAgent
from app.agentic_testing.models import AgentReport


class TestPyritAttackAgentAgent:
    def test_agent_runs(self):
        agent = PyRITAttackAgent()
        report = agent.run()
        assert isinstance(report, AgentReport)
        assert report.status in {'passed', 'warning'}
