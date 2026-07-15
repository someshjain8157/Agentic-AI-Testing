from importlib import import_module


def test_expected_agent_modules_are_available():
    modules = [
        "app.agents",
        "app.agents.base",
        "app.agents.deepeval_agent",
        "app.agents.ragas_agent",
        "app.agents.pyrit_agent",
        "app.agents.playwright_agent",
        "app.orchestrator",
    ]

    for module_name in modules:
        module = import_module(module_name)
        assert module is not None
