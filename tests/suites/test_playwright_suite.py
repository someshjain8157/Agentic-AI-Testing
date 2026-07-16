from app.agentic_testing.agents.playwright_generator import PlaywrightGeneratorAgent


def test_playwright_stub():
    assert True


def test_playwright_agent_generates_related_test_suites():
    agent = PlaywrightGeneratorAgent()
    result = agent.run()

    assert result.name == "playwright_generator_agent"
    assert result.status == "passed"
    assert any(path.endswith("test_chatbot_ui_playwright.py") for path in result.artifacts)
    assert any(path.endswith("test_chatbot_ragas_pytest.py") for path in result.artifacts)
    assert any(path.endswith("test_chatbot_deepeval_pytest.py") for path in result.artifacts)
