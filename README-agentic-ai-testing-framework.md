# Agentic AI testing framework

This document covers the agentic AI testing framework for TeacherAI. It is a multi-agent evaluation layer designed to validate chatbot responses, retrieval grounding, adversarial behavior, and browser-based workflows through Playwright, DeepEval, RAGAS-style retrieval verification, PyRIT, Langfuse, Braintrust, and Guardrails AI.

The framework is built around a single sequential orchestration flow so the whole evaluation pass feels like one pipeline, while still keeping each library-specific check isolated enough to report as its own suite.

## 1. Framework layout

Install the testing dependencies with:

```powershell
pip install -r requirements-agentic.txt
pip install pytest allure-pytest
```

### 1.1 Key files and folders

- `app/testing/orchestrator.py`
  - Main sequential testing pipeline.
- `app/testing/agents/`
  - Contains the explicit agent implementations used by the pipeline.
- `app/testing/agents/golden_dataset.py`
  - Builds golden question-answer datasets from local textbook snippets.
- `app/testing/agents/ragas_agent.py`
  - Runs RAGAS-style retrieval verification against the generated goldens.
- `app/testing/agents/deepeval_agent.py`
  - Runs sample comparisons against the generated golden dataset.
- `app/testing/agents/pyrit_attack.py`
  - Runs adversarial or red-team style checks.
- `app/testing/agents/compliance.py`
  - Contains the Langfuse, Braintrust, and Guardrails-style checks.
- `app/testing/agents/playwright_generator.py`
  - Generates browser and library-specific pytest modules.
- `app/testing/agents/playwright_runner.py`
  - Executes the generated Playwright-oriented pytest files.
- `tests/suites/`
  - Stores separate pytest suites for each library or evaluation area.
- `tests/suites/test_deepeval_suite.py`
  - Pytest suite for the DeepEval flow.
- `tests/suites/test_ragas_suite.py`
  - Pytest suite for the RAGAS flow.
- `tests/suites/test_pyrit_suite.py`
  - Pytest suite for the PyRIT flow.
- `tests/suites/test_playwright_suite.py`
  - Pytest suite for the Playwright browser workflow.
- `tests/suites/test_langfuse_suite.py`
  - Pytest suite for observability checks.
- `tests/suites/test_braintrust_suite.py`
  - Pytest suite for audit and experiment logging checks.
- `tests/suites/test_guardrails_suite.py`
  - Pytest suite for safety and compliance checks.
- `pytest.ini`
  - Configures pytest and the Allure output directory.
- `reports/allure/`
  - Stores the latest Allure report output.

## 2. Agent types in the framework

- Golden dataset agent
  - Generates question-answer pairs from textbook snippets.
- RAGAS agent
  - Compares retrieved answers against the generated goldens.
- DeepEval agent
  - Evaluates chatbot responses against expected quality criteria.
- PyRIT agent
  - Runs adversarial or red-team style checks.
- Langfuse agent
  - Tracks observability and tracing around chatbot evaluations.
- Braintrust agent
  - Supports experiment-style evaluation and logging workflows.
- Guardrails AI agent
  - Validates prompt and output safety constraints.
- Playwright agent
  - Acts as the umbrella browser workflow and generates the browser-facing pytest modules.

## 3. Workflow

The testing workflow is intentionally linear:

1. The orchestrator generates golden datasets.
2. The RAGAS-style retrieval verifier checks retrieval quality against those goldens.
3. DeepEval compares sampled chatbot answers to the expected goldens.
4. PyRIT runs adversarial checks.
5. Langfuse, Braintrust, and Guardrails review observability, audit, and compliance behavior.
6. Playwright generates browser-oriented pytest modules.
7. Playwright executes the generated browser tests.
8. The orchestrator collects the results into a single run report.

## 4. What gets executed and generated

When you run the framework, the following artifacts are produced:

- Executed test modules
  - Pytest suites under `tests/suites/`
- Generated test results
  - Pytest output is collected by pytest and stored in the workspace.
- Allure report
  - HTML-style report written to `reports/allure/`
- Runtime summaries
  - Agent execution summaries are printed in the terminal and also saved as structured JSON in `reports/agentic/`

## 5. Where results are saved

- Test suites: `tests/suites/`
- Pytest output and execution status: terminal output and pytest reports
- Allure report: `reports/allure/`
- Structured agent reports: `reports/agentic/`

## 6. How to run the framework

The orchestrator and the pytest suites do different jobs.

### 6.1 Run the orchestrator

```powershell
python -m app.testing.orchestrator
```

This executes the full agent workflow in one pass.

### 6.2 Run the pytest suites

```powershell
pytest -q tests/suites
```

This runs the formal library-specific test files.

### 6.3 Generate Allure output

```powershell
pytest -q tests/suites --alluredir=reports/allure
```

### 6.4 View the report

```powershell
allure serve reports/allure
```

### 6.5 Run the regression checks used during development

```powershell
pytest -q tests/suites/test_agent_layout.py tests/suites/test_observability.py
```

## 7. Notes

- The newer `app/testing/` package is the clearest place to understand the evaluation workflow.
- The older `app/agents/` package remains as a compatibility layer and mirrors parts of the same intent.
- Each pytest file under `tests/suites/` is intended to act as a separate suite inside the shared Allure report.
