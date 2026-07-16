# TeacherAI

TeacherAI has two parts:

- The chatbot application under `app/`
- The agentic AI testing framework under `app/agentic_testing/` and `tests/`

If you are trying to understand the testing workflow, start with `app/agentic_testing/orchestrator.py`. That is the main single-flow runner.

## 1. Simple Mental Model

Think of the project like this:

```text
Student or test asks a question
        |
        v
TeacherAI chatbot answers from local textbook/RAG context
        |
        v
Agentic testing framework evaluates the answer
        |
        v
Pytest and Allure collect the results as suites
```

The testing workflow now uses `app/agentic_testing/agents/` only. Older compatibility agents were removed so there is one clear place to look.

## 2. Chatbot Application

The chatbot runtime lives in `app/`.

Important files:

- `app/server.py`
  - Starts the FastAPI app.
  - Serves the web page.
  - Exposes endpoints like `/subjects` and `/ask`.
- `app/chatbot.py`
  - Handles chatbot question-answer logic.
  - Calls retrieval and the local model.
- `app/rag.py`
  - Loads textbook PDFs.
  - Builds chunks and embeddings.
  - Retrieves relevant textbook passages.
- `app/config.py`
  - Stores paths, model names, chunk settings, and retrieval configuration.
- `app/index_books.py`
  - Rebuilds or refreshes the book index when subject folders change.
- `app/observability.py`
  - Writes structured operational and audit logs.

## 3. Agentic Testing Workflow

The main command is:

```powershell
python -m app.agentic_testing.orchestrator
```

That command runs this flow:

1. `GoldenDatasetAgent`
   - Reads textbook snippets.
   - Generates golden question-answer datasets.
   - Saves them under `tests/agentic/golden/`.

2. `RagasAgent`
   - Reads the generated golden datasets.
   - Sends golden questions to the chatbot.
   - Compares expected answers with actual chatbot answers.
   - Acts as the RAGAS-style retrieval and answer-quality step.

3. `DeepEvalAgent`
   - Reads golden datasets.
   - Runs sampled chatbot questions.
   - Uses DeepEval metrics when the library is installed.
   - Falls back to a simple comparison when DeepEval is unavailable.

4. `PyRITAttackAgent`
   - Sends adversarial prompts to the chatbot.
   - Checks whether the chatbot leaks hidden instructions, system prompt text, or unsafe content.

5. `LangfuseObservabilityAgent`
   - Reads `logs/agent.jsonl`.
   - Checks whether observability events have useful fields like request IDs and event names.

6. `BraintrustAuditAgent`
   - Reads `logs/audit.jsonl`.
   - Checks whether audit records contain useful evaluation fields.

7. `GuardrailComplianceAgent`
   - Reads audit logs.
   - Looks for policy issues such as PII-like text or missing citations.

8. `PlaywrightGeneratorAgent`
   - Generates pytest files under `tests/agentic/generated/`.
   - Creates browser UI tests and generated tests for golden data, RAGAS, DeepEval, PyRIT, and compliance checks.

9. `PlaywrightRunnerAgent`
   - Runs the generated pytest files.
   - Captures the return code, stdout, and stderr into the agent report.

At the end, the orchestrator writes a combined JSON run report under `reports/agentic/`.

## 4. Files In `app/agentic_testing/`

This is the main testing framework package.

- `app/agentic_testing/orchestrator.py`
  - Runs all testing agents in sequence.
  - Produces one combined run report.
- `app/agentic_testing/__main__.py`
  - Lets you run the workflow with `python -m app.agentic_testing`.
- `app/agentic_testing/models.py`
  - Defines shared data objects such as `AgentReport`, `RunReport`, `GoldenExample`, and `Snippet`.
- `app/agentic_testing/config.py`
  - Defines testing paths like `tests/agentic/golden/`, `tests/agentic/generated/`, and `reports/agentic/`.
- `app/agentic_testing/client.py`
  - Client used by agents to ask questions to the chatbot.
- `app/agentic_testing/llm.py`
  - Local LLM helper used by dataset generation.
- `app/agentic_testing/discovery.py`
  - Finds book folders and builds snippets from textbook content.
- `app/agentic_testing/reporting.py`
  - Saves agent and run reports as JSON.
- `app/agentic_testing/utils.py`
  - Shared utility helpers for JSON, folders, and text normalization.

## 5. Files In `app/agentic_testing/agents/`

These are the real testing agents used by the main workflow.

- `app/agentic_testing/agents/base.py`
  - Base class for all testing agents.
  - Handles timing and failure reporting.
- `app/agentic_testing/agents/golden_dataset.py`
  - Generates golden datasets from textbook snippets.
- `app/agentic_testing/agents/ragas_agent.py`
  - Runs RAGAS-style answer checks against golden datasets.
- `app/agentic_testing/agents/deepeval_agent.py`
  - Runs DeepEval-style response quality checks.
- `app/agentic_testing/agents/pyrit_attack.py`
  - Runs adversarial prompt checks.
- `app/agentic_testing/agents/compliance.py`
  - Contains Langfuse-style, Braintrust-style, and Guardrails-style agents.
- `app/agentic_testing/agents/playwright_generator.py`
  - Generates pytest files for browser and agent checks.
- `app/agentic_testing/agents/playwright_runner.py`
  - Runs generated pytest files.

## 6. Files In `tests/`

The `tests/` folder is for pytest.

- `tests/conftest.py`
  - Sets up default Allure output under `reports/allure/`.
- `tests/suites/test_agent_layout.py`
  - Confirms expected agent modules can be imported.
- `tests/suites/test_deepeval_suite.py`
  - DeepEval suite placeholder/check entry.
- `tests/suites/test_ragas_suite.py`
  - RAGAS suite placeholder/check entry.
- `tests/suites/test_pyrit_suite.py`
  - PyRIT suite placeholder/check entry.
- `tests/suites/test_playwright_suite.py`
  - Checks the active Playwright generator creates related generated suites.
- `tests/suites/test_langfuse_suite.py`
  - Langfuse observability suite placeholder/check entry.
- `tests/suites/test_braintrust_suite.py`
  - Braintrust audit suite placeholder/check entry.
- `tests/suites/test_guardrails_suite.py`
  - Guardrails compliance suite placeholder/check entry.
- `tests/suites/test_observability.py`
  - Tests log redaction, hashing, and audit payload behavior.

Generated tests are written to:

```text
tests/agentic/generated/
```

Golden datasets are written to:

```text
tests/agentic/golden/
```

## 7. Allure Report Flow

To run the pytest suites and create one Allure results folder:

```powershell
pytest -q tests/suites --alluredir=reports/allure
```

To view the report:

```powershell
allure serve reports/allure
```

Each pytest file under `tests/suites/` is treated like a separate suite, so DeepEval, RAGAS, PyRIT, Playwright, Langfuse, Braintrust, and Guardrails can appear separately while still rolling up into one report.

## 8. Setup Commands

Create a virtual environment:

```powershell
cd C:\TeacherAI
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
pip install -r requirements-agentic.txt
```

Start Ollama:

```powershell
ollama pull phi3:mini
ollama serve
```

Start the chatbot:

```powershell
uvicorn app.server:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Run the full testing framework:

```powershell
python -m app.agentic_testing.orchestrator
```
