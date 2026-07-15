# Agentic AI testing framework

This document covers the agentic AI testing framework for TeacherAI. It is a multi-agent, agentic AI evaluation layer designed to validate chatbot responses, retrieval grounding, adversarial behavior, and browser-based workflows through Playwright, DeepEval, RAGAS, PyRIT, Langfuse, Braintrust, and Guardrails AI.

The framework is built around the idea of coordinating specialized agents, each responsible for a different evaluation concern, so the overall testing process is modular, extensible, and closer to real multi-agent AI workflows.

## 1. Framework layout

Install the testing dependencies with:

```powershell
pip install -r requirements-agentic.txt
pip install pytest allure-pytest
```

### 1.1 Key files and folders

- app/agents/
  - Contains one Python module per testing agent.
- app/agents/__init__.py
  - Marks the agent package for imports.
- app/agents/base.py
  - Defines the shared agent interface and result object.
- app/agents/deepeval_agent.py
  - Implements the DeepEval evaluation agent.
- app/agents/ragas_agent.py
  - Implements the RAGAS retrieval and generation evaluation agent.
- app/agents/pyrit_agent.py
  - Implements the PyRIT adversarial testing agent.
- app/agents/playwright_agent.py
  - Implements the Playwright umbrella browser-testing agent that bundles the other agent-related checks into its workflow.
- app/orchestrator.py
  - Executes the agents in a coordinated workflow.
- tests/suites/
  - Stores separate pytest suites for each library or evaluation area.
- tests/suites/test_deepeval_suite.py
  - Pytest suite for the DeepEval agent.
- tests/suites/test_ragas_suite.py
  - Pytest suite for the RAGAS agent.
- tests/suites/test_pyrit_suite.py
  - Pytest suite for the PyRIT agent.
- tests/suites/test_playwright_suite.py
  - Pytest suite for the Playwright umbrella workflow and its embedded agent checks.
- tests/suites/test_langfuse_suite.py
  - Pytest suite for the Langfuse observability and tracing agent.
- tests/suites/test_braintrust_suite.py
  - Pytest suite for the Braintrust experiment and logging agent.
- tests/suites/test_guardrails_suite.py
  - Pytest suite for the Guardrails AI safety and compliance agent.
- pytest.ini
  - Configures pytest and the Allure output directory.
- reports/allure/
  - Stores the latest Allure report output.

## 2. Agent types in the framework

- DeepEval agent
  - Library: deepeval
  - Evaluates chatbot responses against expected quality criteria.
- RAGAS agent
  - Library: ragas
  - Focuses on retrieval-augmented generation quality.
- PyRIT agent
  - Library: pyrit
  - Runs adversarial or red-team style checks.
- Langfuse agent
  - Library: langfuse
  - Tracks observability and tracing around chatbot evaluations.
- Braintrust agent
  - Library: braintrust
  - Supports experiment-style evaluation and logging workflows.
- Guardrails AI agent
  - Library: guardrails-ai
  - Validates prompt and output safety constraints.
- Playwright agent
  - Library: playwright
  - Acts as the umbrella browser-based workflow and embeds the other agent checks into the same run while verifying user journeys such as submitting a question and receiving an answer.

## 3. Workflow

The testing workflow is simple and modular:

1. The orchestrator loads the available agent modules.
2. Each agent runs its own test logic.
3. Every agent produces a result object with a status, summary, and optional artifacts.
4. The orchestrator collects the results and finishes the run.
5. The test outputs and reports are written to the configured folders.

## 4. What gets executed and generated

When you run the framework, the following artifacts are produced:

- Executed test modules
  - pytest suites under tests/suites/
- Generated test results
  - Test result output is collected by pytest and stored in the workspace.
- Allure report
  - HTML-style report written to reports/allure/
- Runtime summaries
  - Agent execution summaries are printed in the terminal and can also be saved as structured output in the reports folder.

## 5. Where results are saved

- Test suites: tests/suites/
- Pytest output and execution status: terminal output and pytest reports
- Allure report: reports/allure/
- Optional structured agent reports: add a dedicated reports/agentic/ folder for machine-readable JSON summaries if you want to persist them long term

## 6. How to run the framework

The orchestrator and the pytest suites do different jobs.

### 6.1 When you run the orchestrator

Running:

```powershell
python -m app.orchestrator
```

executes the full agent workflow in one pass in this order:
1. imports the agent modules from app/agents/
2. creates the agent instances in the orchestrator list
3. runs the agents in this sequence:
   - DeepEvalAgent
   - RagasAgent
   - PyritAgent
   - LangfuseAgent
   - BraintrustAgent
   - GuardrailsAgent
   - PlaywrightAgent
4. collects each agent result
5. prints one summary line per agent result
6. exits with the overall workflow output for that run

Use this when you want to trigger the full agent-based evaluation workflow as a single coordinated run.

### 6.2 When you run the pytest suites

Running:

```powershell
pytest -q tests/suites
```

executes the actual test files under tests/suites/. It will:
- run the pytest-based suite files such as test_deepeval_suite.py, test_ragas_suite.py, test_pyrit_suite.py, test_langfuse_suite.py, test_braintrust_suite.py, test_guardrails_suite.py, and test_playwright_suite.py
- execute the assertions and test cases defined in those suite files
- collect results in pytest output and report them in the terminal
- generate or refresh the Allure report when the Allure directory is configured

Use this when you want to run the formal test suites themselves.

```powershell
pytest -q tests/suites
```

Generate or refresh the Allure report:

```powershell
pytest -q tests/suites --alluredir=reports/allure
```

View the latest Allure report:

```powershell
allure serve reports/allure
```

You can also run the regression checks used during development:

```powershell
pytest -q tests/suites/test_agent_layout.py tests/suites/test_observability.py
```
