# TeacherAI

TeacherAI is a FastAPI-based educational chatbot that answers questions using local textbook PDFs and retrieval-augmented generation. The project also includes an agentic testing framework for validating response quality, retrieval grounding, adversarial behavior, and browser-based workflows.

For the complete agentic AI testing setup, workflow, and reporting guide, see [README-agentic-ai-testing-framework.md](README-agentic-ai-testing-framework.md).

## 1. Chatbot setup and architecture

### 1.1 Prerequisites
- Python 3.10+ (the project is currently running with Python 3.14 in this environment)
- Ollama installed and running locally
- A local virtual environment recommended
- Internet access for the first install of Python packages and Ollama model download

### 1.2 Create a virtual environment
```powershell
cd C:\TeacherAI
python -m venv .venv
.\.venv\Scripts\activate
```

### 1.3 Install project libraries
```powershell
pip install -r requirements.txt
```

### 1.4 Install chatbot and RAG dependencies
If you want the full chatbot stack locally, install the core app packages and the optional agentic testing libraries:

```powershell
pip install -r requirements.txt
pip install -r requirements-agentic.txt
```

### 1.5 Install and run Ollama
If Ollama is not installed yet, install it from https://ollama.com and then pull the model used by the app:

```powershell
ollama pull phi3:mini
ollama serve
```

### 1.6 Project folder structure
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

### 1.7 Add PDF textbooks
Place your textbook PDFs inside the subject folders under books/. Example:

```text
books/
  SCIENCE - Exploration/
    chapter1.pdf
    chapter2.pdf
  ENGLISH- Kaveri/
    chapter1.pdf
```

### 1.8 Create the RAG knowledge base
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

### 1.9 Start the server
```powershell
uvicorn app.server:app --reload
```

Then open:
```text
http://127.0.0.1:8000
```

### 1.10 Chatbot URLs and endpoints

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

### 1.11 Observability, audit, and compliance logging

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

### 1.12 Build the EXE

Use `launch.py` as the PyInstaller entry script. It starts the FastAPI server, waits for it to be ready, and opens the browser for the user.

Build the EXE from the project root:

```powershell
pyinstaller --noconfirm --clean TeacherAI.spec
```

After the build finishes, the executable will be created in:

```text
dist\TeacherAI.exe
```

### 1.13 Run the packaged EXE

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

### 1.14 Files to create or update

#### Required files
- requirements.txt
  - Python dependencies for the project
- .venv/
  - Local virtual environment for the app
- chromadb/
  - Created automatically when the RAG database is built

#### Optional files you may create
- .gitignore
  - Recommended to ignore .venv/, __pycache__/, and chromadb/ if you do not want to commit them
- logs/
  - Optional folder for debugging or runtime logs

### 1.15 How to convert PDFs into RAG content

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

### 1.16 File overview

#### Core app files
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

#### Frontend files
- app/static/app.js
  - Browser-side logic for sending questions, handling streaming responses, and speaking the answer aloud.

- app/templates/index.html
  - Main web page UI for the chatbot.

- app/static/style.css
  - Styles for the app interface, including the avatar layout and image states.

- app/static/avatar/
  - Contains the avatar images used for idle, listening, thinking, and speaking states.

#### Data and utilities
- books/
  - Folder containing subject-wise textbook PDFs.

- chromadb/
  - Persisted vector database created by Chroma.

- app/index_books.py
  - Refresh utility that scans all subject folders under `books/`, reports discovered subjects, and rebuilds Chroma.

- requirements.txt
  - Python dependencies for the project.

### 1.17 How the project works end to end

1. The user opens the web app in the browser.
2. The frontend loads the available subject folders from the backend.
3. When the user asks a question, the browser sends it to the FastAPI /ask endpoint.
4. The backend identifies the type of request (normal answer, math, quiz, MCQ, etc.).
5. For most requests, the app retrieves the most relevant textbook passages from the local PDF knowledge base using RAG.
6. The retrieved textbook context is passed to Ollama along with the user question and task-specific instructions.
7. The model answers using the supplied context, and the response is streamed back to the UI in real time.
8. The frontend displays the answer, shows the source book/chapter/page metadata, and optionally speaks the answer aloud.
9. The conversation is saved in memory for the current session.

## 2. Notes
- The app is designed to work locally and does not depend on a cloud API for answering.
- The quality of responses depends on the quality of the PDF content and the Ollama model selected.
- If you add or replace textbook PDFs, rebuild the Chroma database so the new content is searchable.
