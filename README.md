# TeacherAI

This repository has two different concerns that are easy to mix up:

- The chatbot application itself lives under app/.
- The testing and evaluation framework lives under app/testing/ and tests/.

In short:

- app/ = product code for the chatbot.
- app/agents/ = agent-related modules used by the top-level agent runner.
- app/testing/ = the newer, more explicit testing framework package.
- tests/ = pytest test suite files that exercise the testing framework.

## 1. How to think about the folders

### 1.1 The chatbot app
The runtime application is under app/ and contains the FastAPI server, RAG pipeline, chatbot logic, and frontend assets.

Typical files:
- app/server.py
- app/chatbot.py
- app/rag.py
- app/config.py

### 1.2 The agent-related modules
There is also an app/agents/ package. This is an agent layer for evaluation and orchestration, not the main chatbot runtime.

Typical files:
- app/agents/base.py
- app/agents/deepeval_agent.py
- app/agents/playwright_agent.py

### 1.3 The testing framework
The more explicit testing framework lives under app/testing/. This package contains its own agents, models, reporting, and orchestrator.

Typical files:
- app/testing/orchestrator.py
- app/testing/agents/
- app/testing/reporting.py

### 1.4 Pytest suites
The separate tests/ folder contains pytest suite files that run the testing framework.

Typical files:
- tests/suites/test_deepeval_suite.py
- tests/suites/test_playwright_suite.py
- tests/suites/test_observability.py

## 2. Why there are two agent folders
There are two agent-related packages because the repository contains both:

1. A top-level agent orchestration layer under app/agents/.
2. A fuller testing framework under app/testing/agents/.

They overlap in purpose, but they are not the same thing. The newer testing package is the clearer place to look when you want to understand the evaluation workflow.

## 3. Recommended mental model
If you are new to the repo, use this rule of thumb:

- Open app/ when you want to understand the chatbot product.
- Open app/testing/ when you want to understand the test framework.
- Open tests/ when you want to see the pytest suites.

## 4. Chatbot setup and architecture

### 4.1 Prerequisites
- Python 3.10+
- Ollama installed and running locally
- A local virtual environment recommended

### 4.2 Create a virtual environment
```powershell
cd C:\TeacherAI
python -m venv .venv
.\.venv\Scripts\activate
```

### 4.3 Install dependencies
```powershell
pip install -r requirements.txt
pip install -r requirements-agentic.txt
```

### 4.4 Install and run Ollama
```powershell
ollama pull phi3:mini
ollama serve
```

### 4.5 Start the server
```powershell
uvicorn app.server:app --reload
```

Open:
```text
http://127.0.0.1:8000
```

## 5. Agentic AI testing framework

The testing framework is designed to evaluate chatbot responses, retrieval grounding, adversarial behavior, and browser-based workflows.

### 5.1 Run the full testing workflow
```powershell
python -m app.testing.orchestrator
```

### 5.2 Run pytest suites
```powershell
pytest -q tests/suites
```

### 5.3 Generate Allure output
```powershell
pytest -q tests/suites --alluredir=reports/allure
```

### 5.4 View the report
```powershell
allure serve reports/allure
```
- run the pytest-based suite files such as test_deepeval_suite.py, test_ragas_suite.py, test_pyrit_suite.py, test_langfuse_suite.py, test_braintrust_suite.py, test_guardrails_suite.py, and test_playwright_suite.py
- execute the assertions and test cases defined in those suite files
- collect results in pytest output and report them in the terminal
- generate or refresh the Allure report when the Allure directory is configured

Use this when you want to run the formal test suites themselves.

```powershell
pytest -q tests/suites
```

Generate or refresh the Allure report:

=======
### 5.3 Generate Allure output
>>>>>>> ab9d9f6 (readme updated)
```powershell
pytest -q tests/suites --alluredir=reports/allure
```

<<<<<<< HEAD
View the latest Allure report:

```powershell
allure serve reports/allure
```

You can also run the regression checks used during development:

```powershell
pytest -q tests/suites/test_agent_layout.py tests/suites/test_observability.py
```
=======
### 5.4 View the report
```powershell
allure serve reports/allure
```
>>>>>>> ab9d9f6 (readme updated)
