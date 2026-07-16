from importlib import import_module


def test_expected_agent_modules_are_available():
    modules = [
        "app.agentic_testing",
        "app.agentic_testing.orchestrator",
        "app.agentic_testing.agents",
        "app.agentic_testing.agents.base",
        "app.agentic_testing.agents.golden_dataset",
        "app.agentic_testing.agents.ragas_agent",
        "app.agentic_testing.agents.deepeval_agent",
        "app.agentic_testing.agents.pyrit_attack",
        "app.agentic_testing.agents.compliance",
        "app.agentic_testing.agents.playwright_generator",
        "app.agentic_testing.agents.playwright_runner",
    ]

    for module_name in modules:
        module = import_module(module_name)
        assert module is not None
