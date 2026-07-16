from pathlib import Path
import time
from uuid import uuid4

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.chatbot import ask
from app.rag import discover_subjects
from app.observability import log_event

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Akanksh AI 1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)


@app.middleware("http")
async def request_observability_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid4().hex
    started_at = time.perf_counter()
    request.state.request_id = request_id

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - started_at) * 1000
        response.headers["X-Request-Id"] = request_id
        log_event(
            "http.request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response
    except Exception as exc:
        duration_ms = (time.perf_counter() - started_at) * 1000
        log_event(
            "http.error",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            duration_ms=round(duration_ms, 2),
            error=type(exc).__name__,
        )
        raise


class Question(BaseModel):

    question: str

    subject: str = ""


@app.get("/", response_class=HTMLResponse)
def home():

    html_file = BASE_DIR / "templates" / "index.html"

    return html_file.read_text(encoding="utf-8")

@app.get("/subjects")
def get_subjects():
    return {"subjects": discover_subjects()}

@app.post("/ask")
async def ask_api(data: Question, request: Request):
    request_id = getattr(request.state, "request_id", uuid4().hex)

    log_event(
        "chat.request_received",
        request_id=request_id,
        subject=data.subject,
        question_length=len(data.question),
    )

    async def event_stream():
        async for chunk in ask(data.question, data.subject, request_id=request_id):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/plain")
