from app.agents.playwright_agent import PlaywrightAgent


def test_playwright_stub():
    assert True


def test_playwright_agent_embeds_other_agent_checks():
    agent = PlaywrightAgent()
    result = agent.run()

    assert result.name == "playwright_agent"
    assert result.data["agent_count"] >= 6
    assert any(item["name"] == "deepeval_agent" for item in result.data["embedded_agents"])
    assert any(item["name"] == "ragas_agent" for item in result.data["embedded_agents"])
