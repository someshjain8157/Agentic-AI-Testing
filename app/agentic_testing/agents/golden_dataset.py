from __future__ import annotations

import re

from app.agentic_testing.agents.base import BaseAgent
from app.agentic_testing.config import DEFAULT_GOLDEN_PER_SUBJECT, GOLDEN_DATA_DIR
from app.agentic_testing.discovery import build_snippets_for_family, discover_subject_families
from app.agentic_testing.models import AgentReport, GoldenExample
from app.agentic_testing.reporting import save_agent_report
from app.agentic_testing.utils import ensure_dir, write_json


def _first_sentence(text: str) -> str:
    cleaned = " ".join(text.split()).strip()
    if not cleaned:
        return ""

    match = re.search(r"(.+?[.!?])(?:\s|$)", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned[:220].rstrip()


def _fallback_example(family, snippet, index: int) -> GoldenExample:
    answer = _first_sentence(snippet.text)
    if not answer:
        answer = snippet.text[:220].strip()

    question_templates = [
        "What is the main idea in {chapter}?",
        "What does the excerpt from {chapter} explain?",
        "What does the textbook say about this topic in {chapter}?",
        "Which important point is described in {chapter}?",
    ]
    template = question_templates[(index - 1) % len(question_templates)]
    question = template.format(chapter=snippet.chapter or family.label)

    return GoldenExample(
        id=f"{family.key}_{index}",
        subject_key=family.key,
        subject_label=family.label,
        question=question,
        expected_answer=answer,
        citations=[snippet.citation()],
        source_ids=[snippet.snippet_id],
        difficulty=["easy", "medium", "hard"][(index - 1) % 3],
        task_type="short_answer",
    )


def _coerce_items(payload) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        items = payload.get("items", [])
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
    return []


class GoldenDatasetAgent(BaseAgent):
    name = "golden_dataset_agent"

    def _run(self) -> AgentReport:
        ensure_dir(GOLDEN_DATA_DIR)
        generated_files: list[str] = []
        families = [family for family in discover_subject_families() if family.key in {"math", "social_science", "science", "english"}]
        subject_counts: dict[str, int] = {}

        for family in families:
            snippets = build_snippets_for_family(family, max_snippets=6)
            if not snippets:
                continue

            examples: list[GoldenExample] = []
            seen_questions: set[str] = set()
            for index in range(1, DEFAULT_GOLDEN_PER_SUBJECT + 1):
                snippet = snippets[(index - 1) % len(snippets)]
                example = _fallback_example(family, snippet, index)
                if example.question in seen_questions:
                    continue
                seen_questions.add(example.question)
                examples.append(example)

            subject_counts[family.key] = len(examples)
            generated_path = GOLDEN_DATA_DIR / f"{family.key}.json"
            write_json(generated_path, [example.to_dict() for example in examples])
            generated_files.append(str(generated_path))

        report = AgentReport(
            name=self.name,
            status="passed",
            summary="Golden datasets generated for the core subjects.",
            duration_ms=0.0,
            artifacts=generated_files,
            data={"subjects": subject_counts},
        )
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report

