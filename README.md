# Agentic AI Testing

Agentic AI Testing is a modular framework for evaluating chatbot and RAG systems using separate agent modules for DeepEval, RAGAS, PyRIT, and Playwright. The project also includes pytest-based suites and Allure reporting.

This repository builds on the TeacherAI chatbot app and adds a dedicated testing infrastructure for validating response quality, retrieval grounding, adversarial behavior, and browser-based workflows.

## TeacherAI overview

TeacherAI is a FastAPI-based educational assistant for students. It lets users ask questions about textbook content, get answers with retrieval-augmented generation (RAG), and receive quiz-style or study-help responses grounded in local PDF books.

## 1. Setup

### Prerequisites
- Python 3.10+ (the project is currently running with Python 3.14 in this environment)
- Ollama installed and running locally
- A local virtual environment recommended
- Internet access for the first install of Python packages and Ollama model download

### 1.1 Create a virtual environment
```powershell
cd C:\TeacherAI
python -m venv .venv
.\.venv\Scripts\activate
```

### 1.2 Install project libraries
```powershell
pip install -r requirements.txt
```

### 1.3 Install and run Ollama
If Ollama is not installed yet, install it from https://ollama.com and then pull the model used by the app:

```powershell
ollama pull phi3:mini
ollama serve
```

### 1.4 Project folder structure
```text
TeacherAI/
  app/
    chatbot.py
    config.py
    memory.py
    question_generator.py
    quiz.py
    rag.py
    server.py
    static/
      app.js
      style.css
      avatar/
    templates/
      index.html
  books/
    SCIENCE - Exploration/
    ENGLISH- Kaveri/
    HINDI - Ganga/
    MATH - Ganita Manjari/
    SANSKRIT - Sarada/
    SOCIAL SCIENCE - Understand Society/
  chromadb/
  requirements.txt
  README.md
```

### 1.5 Add PDF textbooks
Place your textbook PDFs inside the subject folders under books/. Example:

```text
books/
  SCIENCE - Exploration/
    chapter1.pdf
    chapter2.pdf
  ENGLISH- Kaveri/
    chapter1.pdf
```

### 1.6 Create the RAG knowledge base
The app uses Chroma and sentence embeddings to retrieve relevant textbook content. Build the knowledge base once before first use:

```powershell
python -m app.rag
```

This will:
- read the PDFs from the books folder
- split them into chunks
- create or update the vector database in chromadb/

If you add a new folder under `books/`, run:

```powershell
python -m app.index_books
```

That command scans every subject folder again, discovers the new folder automatically, and rebuilds Chroma so the new subject is searchable.

### 1.6.1 Run the agentic test framework

The agentic test lab now has a modular layout under `app/agents/` and `app/orchestrator.py` so each agent type can live in its own module. A dedicated test suite layout also sits under `tests/suites/`.

Run the orchestrator with:

```powershell
python -m app.orchestrator
```

This will execute the separate agent modules for:
- DeepEval
- RAGAS
- PyRIT
- Langfuse
- Braintrust
- Guardrails AI
- Playwright

For the optional third-party evaluation libraries, install:

```powershell
pip install -r requirements-agentic.txt
```

### 1.7 Start the server
```powershell
uvicorn app.server:app --reload
```

Then open:
```text
http://127.0.0.1:8000
```

### 1.8 Chatbot URLs and endpoints

Once the server is running, these are the main browser/API entry points:

- `http://127.0.0.1:8000`
  - Main chatbot web page served by FastAPI.
- `http://127.0.0.1:8000/docs`
  - FastAPI Swagger UI for testing the API directly in the browser.
- `GET /subjects`
  - Returns the available subject folder names from `books/`.
- `POST /ask`
  - Streams the chatbot answer.
  - Example request body:

```json
{
  "question": "Explain photosynthesis",
  "subject": "SCIENCE - Exploration"
}
```

The `/ask` endpoint returns a streaming plain-text response, so it is best used from the web UI or the Swagger docs page.

### 1.9 Observability, audit, and compliance logging

TeacherAI now records structured logs for:

- HTTP request timing and status
- agent request metadata and lifecycle events
- retrieval timing and source counts
- one combined audit record per chat turn
- errors with request correlation IDs

By default, the app logs metadata only and avoids storing raw student text in the audit trail.

Environment variables:

- `TEACHERAI_LOG_LEVEL`
  - Controls the application log level. Default: `INFO`
- `TEACHERAI_LOG_CONTENT`
  - Set to `1`, `true`, or `yes` to include raw question and answer text in the audit log.
  - Keep this off for most compliance-focused deployments.

Audit output:

- `logs/agent.jsonl`
  - Operational observability events for the agent.
- `logs/audit.jsonl`
  - One JSON event per chat turn, stored as JSONL.
  - Each event includes the question, answer, citations, and error details, plus a request ID so you can correlate browser request, backend processing, retrieval, answer, and citations.

### 1.10 Build the EXE

Use `launch.py` as the PyInstaller entry script. It starts the FastAPI server, waits for it to be ready, and opens the browser for the user.

Build the EXE from the project root:

```powershell
pyinstaller --noconfirm --clean TeacherAI.spec
```

After the build finishes, the executable will be created in:

```text
dist\TeacherAI.exe
```

### 1.11 Run the packaged EXE

For a non-technical user, the app should be distributed as a folder that contains the EXE plus the local data it needs.

Recommended folder layout:

```text
TeacherAI Folder/
  TeacherAI.exe
  books/
  chromadb/
```

How to use it:

1. Make sure Ollama is installed and running on the same computer.
2. Open the folder that contains `TeacherAI.exe`.
3. Double-click `TeacherAI.exe`.
4. Wait a few seconds while the local server starts.
5. The browser opens automatically to `http://127.0.0.1:8000`.
6. Ask questions in the chatbot page.

If `books/` is missing, the chatbot will not have textbook content to search.
If `chromadb/` is missing, it can be created again when the app rebuilds the local index.
If Ollama is not running, the EXE will show an error and stop.

## 2. Files to create or update

### Required files
- requirements.txt
  - Python dependencies for the project
- .venv/
  - Local virtual environment for the app
- chromadb/
  - Created automatically when the RAG database is built

### Optional files you may create
- .gitignore
  - Recommended to ignore .venv/, __pycache__/, and chromadb/ if you do not want to commit them
- logs/
  - Optional folder for debugging or runtime logs

## 3. How to convert PDFs into RAG content

The app does not use a manual PDF-to-RAG conversion step. Instead, it automatically processes PDFs when you run:

```powershell
python -m app.rag
```

That command will:
1. scan all PDF files inside the books/ folder
2. extract text from each page
3. split the text into chunks
4. generate embeddings
5. store the vector database in chromadb/

If you add new books or replace existing PDFs, run the same command again so the search index is updated.

## 4. File overview

### Core app files
- app/server.py
  - Starts the FastAPI app.
  - Serves the frontend HTML, exposes the /subjects endpoint, and handles the /ask streaming API.

- app/chatbot.py
  - Main conversation logic.
  - Detects the request type, retrieves relevant textbook context, and streams the answer from Ollama.

- app/rag.py
  - Implements the retrieval layer.
  - Reads PDFs, splits them into chunks, stores them in Chroma, and retrieves the most relevant chunks for a student question.

- app/config.py
  - Central configuration for project paths, model names, chunk size, overlap, and retrieval count.

- app/question_generator.py
  - Converts student requests into prompt instructions.
  - Detects whether the user wants a normal answer, math help, MCQ, quiz, true/false, or revision notes.

- app/memory.py
  - Stores recent conversation history in memory for the active session.

- app/quiz.py
  - Tracks the current in-memory quiz state.

### Frontend files
- app/static/app.js
  - Browser-side logic for sending questions, handling streaming responses, and speaking the answer aloud.

- app/templates/index.html
  - Main web page UI for the chatbot.

- app/static/style.css
  - Styles for the app interface, including the avatar layout and image states.

- app/static/avatar/
  - Contains the avatar images used for idle, listening, thinking, and speaking states.

### Data and utilities
- books/
  - Folder containing subject-wise textbook PDFs.

- chromadb/
  - Persisted vector database created by Chroma.

- app/index_books.py
  - Refresh utility that scans all subject folders under `books/`, reports discovered subjects, and rebuilds Chroma.

- app/agents/
  - Separate agent modules for DeepEval, RAGAS, PyRIT, and Playwright.
- app/orchestrator.py
  - Central orchestrator that runs the agent modules.
- tests/suites/
  - Separate pytest suites for DeepEval, RAGAS, PyRIT, and Playwright.
- pytest.ini
  - Pytest configuration with Allure output enabled.
- reports/allure/
  - Generated Allure report output directory.

- requirements.txt
  - Python dependencies for the project.

## 3. How the project works end to end

1. The user opens the web app in the browser.
2. The frontend loads the available subject folders from the backend.
3. When the user asks a question, the browser sends it to the FastAPI /ask endpoint.
4. The backend identifies the type of request (normal answer, math, quiz, MCQ, etc.).
5. For most requests, the app retrieves the most relevant textbook passages from the local PDF knowledge base using RAG.
6. The retrieved textbook context is passed to Ollama along with the user question and task-specific instructions.
7. The model answers using the supplied context, and the response is streamed back to the UI in real time.
8. The frontend displays the answer, shows the source book/chapter/page metadata, and optionally speaks the answer aloud.
9. The conversation is saved in memory for the current session.

## 4. Chatbot testing framework

TeacherAI includes a dedicated testing framework for validating the chatbot end to end. It is organized into separate agent modules, test suites, and report outputs so each evaluation type can be run independently or together.

### 4.1 Framework layout

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
  - Implements the Playwright browser-testing agent.
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
  - Pytest suite for the Playwright agent.
- pytest.ini
  - Configures pytest and the Allure output directory.
- reports/allure/
  - Stores the latest Allure report output.

### 4.2 Agents in the framework

Each agent is responsible for a different testing concern:

- DeepEval agent
  - Evaluates chatbot responses against expected quality criteria.
  - Useful for comparing answer relevance, structure, and correctness.
- RAGAS agent
  - Focuses on retrieval-augmented generation quality.
  - Checks whether the retrieved context supports the answer well.
- PyRIT agent
  - Runs adversarial or red-team style checks.
  - Helps discover weak spots in prompts, safety behavior, or robustness.
- Langfuse agent
  - Tracks observability and tracing around chatbot evaluations.
  - Useful for monitoring evaluation runs and debugging flows.
- Braintrust agent
  - Supports experiment-style evaluation and logging workflows.
  - Useful for recording and reviewing test outcomes.
- Guardrails AI agent
  - Validates prompt and output safety constraints.
  - Helps enforce compliance and guardrail behavior.
- Playwright agent
  - Executes browser-based UI tests for the chatbot experience.
  - Useful for verifying the web app behavior from a user perspective.

### 4.3 Workflow

The testing workflow is simple and modular:

1. The orchestrator loads the available agent modules.
2. Each agent runs its own test logic.
3. Every agent produces a result object with a status, summary, and optional artifacts.
4. The orchestrator collects the results and finishes the run.
5. The test outputs and reports are written to the configured folders.

### 4.4 What gets executed and generated

When you run the framework, the following artifacts are produced:

- Executed test modules
  - pytest suites under tests/suites/
- Generated test results
  - Test result output is collected by pytest and stored in the workspace.
- Allure report
  - HTML-style report written to reports/allure/
- Runtime summaries
  - Agent execution summaries are printed in the terminal and can also be saved as structured output in the reports folder.

### 4.5 Where results are saved

- Test suites: tests/suites/
- Pytest output and execution status: terminal output and pytest reports
- Allure report: reports/allure/
- Optional structured agent reports: add a dedicated reports/agentic/ folder for machine-readable JSON summaries if you want to persist them long term

### 4.6 How each agent works

- DeepEval agent
  - Runs evaluation checks against the chatbot response quality.
  - Best used when you want to compare generated answers against expected patterns or rubric-based quality checks.
- RAGAS agent
  - Validates retrieval quality for the RAG pipeline.
  - Helps ensure the chatbot is grounded in the right textbook content.
- PyRIT agent
  - Simulates adversarial prompts or attack-style inputs.
  - Useful for checking security, resilience, and prompt robustness.
- Langfuse agent
  - Adds observability and trace-based diagnostics for evaluation runs.
- Braintrust agent
  - Supports structured evaluation logging and experimentation.
- Guardrails AI agent
  - Enforces prompt and response safety constraints during tests.
- Playwright agent
  - Connects to the running app in a browser and verifies key user journeys such as submitting a question and receiving an answer.

### 4.7 How to run the framework

Run the orchestrator:

```powershell
python -m app.orchestrator
```

Run the pytest suites directly:

```powershell
pytest -q tests/suites
```

View the latest Allure report:

```powershell
allure serve reports/allure
```

## 5. Notes
- The app is designed to work locally and does not depend on a cloud API for answering.
- The quality of responses depends on the quality of the PDF content and the Ollama model selected.
- If you add or replace textbook PDFs, rebuild the Chroma database so the new content is searchable.
