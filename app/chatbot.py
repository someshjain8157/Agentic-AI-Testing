import asyncio
import json
import time

import ollama

from app.memory import add
from app.question_generator import build_instruction, detect_request
from app.config import OLLAMA_MODEL, TOP_K
from app.rag import retrieve_documents
from app.observability import audit_payload, log_audit, log_event


SHORT_SUBJECTS = {
    "SCIENCE - Exploration",
    "ENGLISH- Kaveri",
    "SOCIAL SCIENCE - Understand Society",
}


def get_answer_length_guidance(subject: str, request_type: str) -> str:
    if request_type == "math":
        return "Keep the answer very short, ideally under 40 words unless the question asks for more detail."

    if subject in SHORT_SUBJECTS:
        return "Keep the answer around 50-60 words max."

    return "Keep the answer to 2-3 sentences and under 60 words."


# -----------------------------
# Async Ask Function (Streaming)
# -----------------------------
async def ask(question: str, subject: str = "", request_id: str = ""):
    started_at = time.perf_counter()
    request_type = detect_request(question)
    answer_length_guidance = get_answer_length_guidance(subject, request_type)
    instruction = build_instruction(request_type)
    answer = ""
    sources = []
    retrieval_k = 0
    retrieved_chunks = 0
    context = ""
    retrieval_ms = None
    generation_ms = None

    log_event(
        "chat.request_started",
        request_id=request_id,
        subject=subject,
        request_type=request_type,
        question_length=len(question),
        model=OLLAMA_MODEL,
    )

    if request_type == "math":
        chat_options = {
            "temperature": 0.2,
            "num_predict": 96,
        }
        messages = [
            {
                "role": "system",
                "content": f"""
                You are Akanksh AI 1.0.
                You are a concise math helper for students.

                Rules:
                - Solve the math question directly.
                - Do not mention textbooks or retrieval.
                - Keep the answer very short.
                - If a sequence pattern is asked, state the pattern and the next terms.

                Task rules:
                {instruction}
                """,
            },
            {
                "role": "user",
                "content": question,
            },
        ]
    else:
        retrieval_k = TOP_K

        # Run retrieval in a background thread so the event loop stays responsive.
        retrieval_started_at = time.perf_counter()
        retrieval = await asyncio.to_thread(
            retrieve_documents,
            question,
            subject,
            retrieval_k,
        )
        retrieval_ms = (time.perf_counter() - retrieval_started_at) * 1000

        context = retrieval["context"]
        sources = retrieval["sources"]

        retrieved_chunks = len(retrieval["docs"])
        log_event(
            "chat.retrieval_complete",
            request_id=request_id,
            subject=subject,
            request_type=request_type,
            retrieval_k=retrieval_k,
            retrieved_chunks=retrieved_chunks,
            source_count=len(sources),
            context_chars=len(context),
            retrieval_ms=round(retrieval_ms, 2),
        )

        if not context.strip():
            duration_ms = (time.perf_counter() - started_at) * 1000
            log_audit(
                "chat.turn_complete",
                **audit_payload(
                    request_id=request_id,
                    question=question,
                    subject=subject,
                    request_type=request_type,
                    model=OLLAMA_MODEL,
                    citations=[],
                    retrieval_k=retrieval_k,
                    retrieved_chunks=retrieved_chunks,
                    source_count=len(sources),
                    context_chars=len(context),
                    answer="I couldn't find that information in the Grade 9 textbooks.",
                    status="no_context",
                    duration_ms=duration_ms,
                    retrieval_ms=retrieval_ms,
                ),
            )
            yield "I couldn't find that information in the Grade 9 textbooks."
            yield f"\n\n[SOURCES]{json.dumps([])}"
            return

        if request_type in ["mcq", "quiz"]:
            instruction += f"""
            Student Request:
            {question}

            Generate exactly what the student requested.
            Generate only 3 questions unless the student requested more.
            Do not generate extra questions.
            Follow formatting exactly.
            """

        messages = [
            {
                "role": "system",
                "content": f"""
                You are Akanksh AI 1.0.
                You are an AI assistant for Grade 9 students.

                Rules:
                - Use only the TEXTBOOK CONTEXT provided below.
                - Do not use prior knowledge, memory, or outside facts.
                - Answer directly without restating the question or adding an intro.
                - Start with the answer itself.
                - If the context contains relevant information, answer from it even if the exact wording is not present.
                - Only say "I couldn't find that information in the Grade 9 textbooks." when the retrieved context is empty or clearly unrelated.
                - {answer_length_guidance}
                - For MCQ, quiz, true/false, fill-in-the-blank, short answer, long answer, and revision requests, follow the requested format exactly.
                - Prefer the most relevant facts from the first few context chunks.

                Task rules:
                {instruction}
                """,
            },
            {
                "role": "user",
                "content": f"""
                TEXTBOOK CONTEXT
                {context}

                STUDENT REQUEST
                {question}

            Important:
            - Answer using only the TEXTBOOK CONTEXT.
            - If the context is relevant but not perfectly worded, answer with the closest supported textbook meaning.
            - Use the fallback sentence only if the context is empty or unrelated.
            - {answer_length_guidance}
            """,
        },
    ]

        chat_options = {
            "temperature": 0.2,
            "num_predict": 180,
        }

    # -----------------------------
    # Ollama Chat Streaming
    # -----------------------------
    loop = asyncio.get_running_loop()

    def run_chat():
        return ollama.chat(model=OLLAMA_MODEL, messages=messages, stream=True, options=chat_options)

    try:
        response_stream = await loop.run_in_executor(None, run_chat)

        answer_chunks = []
        generation_started_at = time.perf_counter()
        for chunk in response_stream:
            text = chunk["message"]["content"]
            answer_chunks.append(text)
            yield text  # stream each chunk to FastAPI/UI

        generation_ms = (time.perf_counter() - generation_started_at) * 1000
        answer = "".join(answer_chunks)

        # Save conversation
        add("user", question)
        add("assistant", answer)

        log_audit(
            "chat.turn_complete",
            **audit_payload(
                request_id=request_id,
                question=question,
                subject=subject,
                request_type=request_type,
                model=OLLAMA_MODEL,
                citations=sources,
                retrieval_k=retrieval_k or None,
                retrieved_chunks=retrieved_chunks or None,
                source_count=len(sources),
                context_chars=len(context) if context else 0,
                answer=answer,
                status="success",
                duration_ms=(time.perf_counter() - started_at) * 1000,
                retrieval_ms=retrieval_ms,
                generation_ms=generation_ms,
            ),
        )

        log_event(
            "chat.request_finished",
            request_id=request_id,
            subject=subject,
            request_type=request_type,
            answer_length=len(answer),
            source_count=len(sources),
            duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
        )

        # At the end, yield sources marker as JSON for the frontend.
        yield f"\n\n[SOURCES]{json.dumps(sources)}"
    except Exception as exc:
        duration_ms = (time.perf_counter() - started_at) * 1000
        log_event(
            "chat.request_failed",
            request_id=request_id,
            subject=subject,
            request_type=request_type,
            error=type(exc).__name__,
            duration_ms=round(duration_ms, 2),
        )
        log_audit(
            "chat.turn_complete",
            **audit_payload(
                request_id=request_id,
                question=question,
                subject=subject,
                request_type=request_type,
                model=OLLAMA_MODEL,
                citations=sources,
                retrieval_k=retrieval_k or None,
                retrieved_chunks=retrieved_chunks or None,
                source_count=len(sources),
                context_chars=len(context) if context else 0,
                answer=answer or None,
                status="error",
                duration_ms=duration_ms,
                retrieval_ms=retrieval_ms,
                generation_ms=generation_ms,
                error=type(exc).__name__,
            ),
        )
        raise
