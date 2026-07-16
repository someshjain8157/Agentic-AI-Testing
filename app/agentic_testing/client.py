from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient

from app.server import app


@dataclass
class ChatTurn:
    question: str
    subject: str
    answer: str
    sources: list[dict[str, Any]]
    raw_text: str


class ChatbotClient:
    def __init__(self, client: TestClient | None = None):
        self.client = client or TestClient(app)

    def get_subjects(self) -> list[str]:
        response = self.client.get("/subjects")
        response.raise_for_status()
        return response.json().get("subjects", [])

    def ask(self, question: str, subject: str = "") -> ChatTurn:
        response = self.client.post("/ask", json={"question": question, "subject": subject})
        response.raise_for_status()
        raw_text = response.text
        answer_text, sources = self._split_answer_and_sources(raw_text)
        return ChatTurn(
            question=question,
            subject=subject,
            answer=answer_text,
            sources=sources,
            raw_text=raw_text,
        )

    @staticmethod
    def _split_answer_and_sources(raw_text: str) -> tuple[str, list[dict[str, Any]]]:
        marker = "[SOURCES]"
        if marker not in raw_text:
            return raw_text.strip(), []

        answer_text, sources_text = raw_text.split(marker, 1)
        try:
            sources = json.loads(sources_text.strip())
        except json.JSONDecodeError:
            sources = []
        return answer_text.strip(), sources

