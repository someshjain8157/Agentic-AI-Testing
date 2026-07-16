from __future__ import annotations

current_quiz = None


def start(mcqs):
    global current_quiz
    current_quiz = {
        "questions": mcqs,
        "index": 0,
        "score": 0,
    }


def get():
    return current_quiz


def clear():
    global current_quiz
    current_quiz = None
