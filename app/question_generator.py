from __future__ import annotations

import re


def detect_request(question: str) -> str:
    text = question.lower().strip()

    math_markers = (
        "solve",
        "calculate",
        "find",
        "sum",
        "product",
        "difference",
        "quotient",
        "equation",
        "factor",
        "math",
        "algebra",
    )
    if any(marker in text for marker in math_markers) or re.search(r"\d\s*[\+\-\*/=]\s*\d", text):
        return "math"

    if any(token in text for token in ("multiple choice", "mcq", "options", "choose the correct")):
        return "mcq"

    if any(token in text for token in ("quiz", "test me", "practice questions")):
        return "quiz"

    if any(token in text for token in ("true or false", "true/false")):
        return "true_false"

    if any(token in text for token in ("fill in the blank", "fill the blank", "blank")):
        return "fill_in_blank"

    if any(token in text for token in ("short answer", "in brief", "briefly", "2 marks")):
        return "short_answer"

    if any(token in text for token in ("long answer", "explain in detail", "essay", "5 marks", "10 marks")):
        return "long_answer"

    if any(token in text for token in ("revise", "revision", "summary", "notes")):
        return "revision"

    return "normal"


def build_instruction(request_type: str) -> str:
    base = {
        "math": "Solve the problem clearly and directly.",
        "mcq": "Create multiple-choice questions with four options and one correct answer.",
        "quiz": "Create a short quiz with clear questions and answers.",
        "true_false": "Write statements that can be answered true or false.",
        "fill_in_blank": "Write fill-in-the-blank items with the missing word omitted.",
        "short_answer": "Give a concise answer suitable for a short-response question.",
        "long_answer": "Give a fuller, well-structured answer.",
        "revision": "Summarize the topic in revision-friendly bullet points.",
        "normal": "Answer the student's question directly and clearly.",
    }

    return base.get(request_type, base["normal"])
