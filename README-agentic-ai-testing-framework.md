# TeacherAI Agentic AI Testing Framework

This repository contains a multi-agent evaluation framework for TeacherAI. The framework runs dataset generation, chatbot evaluation, red-team checks, observability checks, compliance checks, generated smoke tests, and pytest-based reporting into one combined Allure view.

The chatbot documentation lives in `README-teacherai-chatbot.md`. This file and `README.md` describe the agentic testing workflow only.

## 1. What the framework does

The agentic pipeline is built to:

- generate golden datasets from textbook snippets
- evaluate chatbot answers against those goldens
- compare retrieval quality and response quality
- run adversarial and compliance checks
- generate and reuse smoke-test pytest files
- publish everything into one Allure report

Think of the workflow like this:

```text
Golden data is generated once
        |
        v
Agent tests call the chatbot or inspect logs
        |
        v
Each agent saves a JSON report under reports/agentic/
        |
        v
Pytest suites turn the agent results into Allure test cases
        |
        v
Generated smoke tests and suite tests roll up into one Allure report
```

## 2. Main files

- `app/agentic_testing/orchestrator.py`
  - Runs all agents in sequence.
  - Saves the combined run report.
- `app/agentic_testing/agents/`
  - Contains the concrete agent implementations.
- `app/agentic_testing/client.py`
  - Client wrapper used by evaluation agents to call the chatbot API.
- `app/agentic_testing/llm.py`
  - Direct Ollama helper for agent-side model calls if needed.
- `app/agentic_testing/discovery.py`
  - Discovers subject families and builds snippets for golden data.
- `app/agentic_testing/reporting.py`
  - Writes agent and run reports to JSON files.
- `app/agentic_testing/models.py`
  - Defines `AgentReport`, `RunReport`, `GoldenExample`, `Snippet`, and `SubjectFamily`.
- `tests/suites/`
  - Detailed pytest suites that expose per-agent testcases in Allure.
- `tests/agentic/generated/`
  - Generated smoke-test files reused by default.
- `reports/agentic/`
  - Saved JSON outputs from each agent and the overall run.
- `reports/allure/`
  - Combined Allure results folder produced by pytest.

## 3. Agents and their roles

- `GoldenDatasetAgent`
  - Builds golden question-answer datasets from textbook snippets.
- `RagasAgent`
  - Evaluates retrieval quality using the chatbot response and golden answers.
- `DeepEvalAgent`
  - Compares chatbot answers against golden references and records sample scores.
- `PyRITAttackAgent`
  - Sends adversarial prompts to the chatbot and flags leakage.
- `LangfuseObservabilityAgent`
  - Checks observability log coverage in `logs/agent.jsonl`.
- `BraintrustAuditAgent`
  - Checks audit log coverage in `logs/audit.jsonl`.
- `GuardrailComplianceAgent`
  - Scans audit logs for policy issues such as missing citations or PII-like text.
- `PlaywrightGeneratorAgent`
  - Generates or reuses smoke-test pytest files under `tests/agentic/generated/`.
- `PlaywrightRunnerAgent`
  - Runs the generated smoke-test files with pytest.

## 4. Request flow

There are two model-call paths in the codebase.

### 4.1 Chatbot evaluation path

Used by the evaluation agents:

```text
ChatbotClient.ask()
    -> FastAPI /ask endpoint
        -> app.chatbot.ask()
            -> ollama.chat()
```

This path is used by:

- `DeepEvalAgent`
- `RagasAgent`
- `PyRITAttackAgent`
- generated golden tests

### 4.2 Direct agent LLM path

Available for agent-side direct calls:

```text
BaseAgent.llm
    -> LocalAgentLLM
        -> complete() / complete_json()
            -> ollama.chat()
```

In the current codebase, the concrete evaluation agents mostly use `self.client.ask(...)` rather than `self.llm`.

## 5. Reports generated

Each agent writes a JSON report into `reports/agentic/`.

Examples:

- `golden_dataset_agent.json`
- `ragas_agent.json`
- `deepeval_agent.json`
- `pyrit_attack_agent.json`
- `langfuse_observability_agent.json`
- `braintrust_audit_agent.json`
- `guardrail_compliance_agent.json`
- `playwright_generator_agent.json`
- `playwright_runner_agent.json`
- `run_<id>.json`

These reports are the source data for the suite tests and the combined Allure output.

## 6. Test layers

There are two test layers:

### 6.1 Detailed suite tests

Files under `tests/suites/` read the saved agent JSON reports and turn each agent testcase into a pytest item. In Allure, each item shows:

- testcase name
- expected output
- actual output
- score
- pass or fail
- extra details such as question text, sources, and report metadata

Important suite files:

- `tests/suites/test_golden_dataset_suite.py`
- `tests/suites/test_ragas_suite.py`
- `tests/suites/test_deepeval_suite.py`
- `tests/suites/test_pyrit_suite.py`
- `tests/suites/test_langfuse_suite.py`
- `tests/suites/test_braintrust_suite.py`
- `tests/suites/test_guardrails_suite.py`
- `tests/suites/test_playwright_suite.py`

### 6.2 Generated smoke tests

Files under `tests/agentic/generated/` are lightweight smoke tests. They check that each generated agent wrapper can run and return an `AgentReport`.

They are reused by default. They are regenerated only when the orchestrator is run with:

```powershell
--regenerate-playwright-tests
```

## 7. Allure report layout

The pytest run produces one combined Allure results folder in `reports/allure/`.

The report is intended to show two sections:

- Smoke tests
  - generated pytest wrappers and runner checks
- Agentic evaluation
  - per-agent testcase reporting for golden data, RAGAS, DeepEval, PyRIT, observability, audit, and guardrails

Each agent testcase should appear with its score and pass/fail result, so the Allure report can be used as a readable execution summary.

## 8. Execution

From the project root, run:

```powershell
.\.venv\Scripts\python.exe -m app.agentic_testing.orchestrator
.\.venv\Scripts\python.exe -m pytest -q tests
allure serve reports/allure
```

What each step does:

1. `app.agentic_testing.orchestrator`
   - Generates or reuses golden data.
   - Runs all agents in sequence.
   - Saves reports under `reports/agentic/`.
   - Reuses generated smoke tests unless regeneration is explicitly requested.

2. `pytest -q tests`
   - Runs the detailed agent suites under `tests/suites/`.
   - Runs the generated smoke tests under `tests/agentic/generated/`.
   - Produces the Allure result files in `reports/allure/`.

3. `allure serve reports/allure`
   - Opens the combined report in the browser.

To force regeneration of the generated smoke tests:

```powershell
.\.venv\Scripts\python.exe -m app.agentic_testing.orchestrator --regenerate-playwright-tests
```

## 9. Generated data locations

- Golden datasets:
  - `tests/agentic/golden/`
- Generated smoke tests:
  - `tests/agentic/generated/`
- Agent reports:
  - `reports/agentic/`
- Allure output:
  - `reports/allure/`

## 10. Notes

- Golden datasets are generated once and reused until explicitly regenerated.
- Generated smoke tests are reused by default and only refreshed when requested.
- The detailed suites are the best place to inspect testcase-level score and pass/fail behavior.
- The generated smoke tests are useful as a quick execution check, while the suite tests provide the richer Allure breakdown.
