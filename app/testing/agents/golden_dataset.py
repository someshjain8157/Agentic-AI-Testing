from __future__ import annotations

import textwrap
from pathlib import Path

from app.testing.agents.base import BaseAgent
from app.testing.config import DEFAULT_GOLDEN_PER_SUBJECT, GOLDEN_DATA_DIR
from app.testing.discovery import build_snippets_for_family, discover_subject_families
from app.testing.models import AgentReport, GoldenExample
from app.testing.reporting import save_agent_report
from app.testing.utils import ensure_dir, write_json


SYSTEM_PROMPT = """You are a dataset generation agent for a school chatbot.
Use only the textbook excerpts provided by the user.
Generate concise, student-friendly questions and answers.
Return strict JSON only.
"""


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

            snippet_block = "\n\n".join(
                textwrap.dedent(
                    f"""
                    [{snippet.snippet_id}] subject={snippet.folder_name} chapter={snippet.chapter} page={snippet.page}
                    {snippet.text}
                    """
                ).strip()
                for snippet in snippets
            )

            prompt = f"""
Create exactly {DEFAULT_GOLDEN_PER_SUBJECT} unique question-answer pairs for the {family.label} chatbot.
Questions must be answerable from the excerpts below.
Each item must include:
- question
- expected_answer
- source_ids (one or more snippet ids)
- difficulty (easy, medium, hard)
- task_type

Rules:
- Use only the excerpt content.
- Keep answers short and accurate.
- Prefer school-friendly language.
- Do not add any extra commentary outside JSON.

Textbook excerpts:
{snippet_block}
"""
            payload = self.llm.complete_json(SYSTEM_PROMPT, prompt)
            items = payload if isinstance(payload, list) else payload.get("items", [])

            examples: list[GoldenExample] = []
            for index, item in enumerate(items[:DEFAULT_GOLDEN_PER_SUBJECT], start=1):
                source_ids = item.get("source_ids", [])
                citations = []
                for source_id in source_ids:
                    match = next((snippet for snippet in snippets if snippet.snippet_id == source_id), None)
                    if match:
                        citations.append(match.citation())
                examples.append(
                    GoldenExample(
                        id=f"{family.key}_{index}",
                        subject_key=family.key,
                        subject_label=family.label,
                        question=str(item.get("question", "")).strip(),
                        expected_answer=str(item.get("expected_answer", "")).strip(),
                        citations=citations,
                        source_ids=[str(source_id) for source_id in source_ids],
                        difficulty=str(item.get("difficulty", "medium")),
                        task_type=str(item.get("task_type", "short_answer")),
                    )
                )

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

