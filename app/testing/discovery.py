from collections import defaultdict
from pathlib import Path
from typing import Iterable

from app.config import BOOKS_DIR
from app.rag import load_all_books
from app.testing.config import CANONICAL_SUBJECTS
from app.testing.models import Snippet, SubjectFamily
from app.testing.utils import slugify


def discover_book_folders() -> list[Path]:
    if not BOOKS_DIR.exists():
        return []
    return [folder for folder in sorted(BOOKS_DIR.iterdir()) if folder.is_dir()]


def _match_subject_key(folder_name: str) -> str | None:
    normalized = folder_name.lower()
    if "social science" in normalized:
        return "social_science"
    if normalized.startswith("math") or " math " in normalized or normalized == "math":
        return "math"
    if normalized.startswith("science") or " science " in normalized or normalized == "science":
        return "science"
    if normalized.startswith("english") or " english " in normalized or normalized == "english":
        return "english"
    return None


def discover_subject_families() -> list[SubjectFamily]:
    folders = discover_book_folders()
    grouped: dict[str, list[str]] = defaultdict(list)
    labels: dict[str, str] = {}

    for folder in folders:
        key = _match_subject_key(folder.name)
        if key is None:
            key = slugify(folder.name)
            labels[key] = folder.name
        else:
            labels[key] = CANONICAL_SUBJECTS[key]
        grouped[key].append(folder.name)

    families = [
        SubjectFamily(key=key, label=labels.get(key, key.replace("_", " ").title()), folder_names=sorted(folder_names))
        for key, folder_names in sorted(grouped.items(), key=lambda item: item[0])
    ]
    return families


def get_family_by_key(key: str) -> SubjectFamily | None:
    for family in discover_subject_families():
        if family.key == key:
            return family
    return None


def get_subject_docs(folder_names: Iterable[str]) -> list:
    all_docs = load_all_books()
    wanted = set(folder_names)
    return [doc for doc in all_docs if doc.metadata.get("subject") in wanted]


def build_snippets_for_family(family: SubjectFamily, max_snippets: int = 6, max_chars: int = 700) -> list[Snippet]:
    docs = get_subject_docs(family.folder_names)
    snippets: list[Snippet] = []
    seen_chapters: set[tuple[str, str]] = set()
    counter = 1

    for doc in docs:
        chapter = str(doc.metadata.get("chapter", ""))
        folder_name = str(doc.metadata.get("subject", family.label))
        key = (folder_name, chapter)
        if key in seen_chapters:
            continue
        seen_chapters.add(key)

        text = " ".join(doc.page_content.split())
        if not text:
            continue

        snippets.append(
            Snippet(
                snippet_id=f"{family.key[:3].upper()}{counter}",
                subject_key=family.key,
                folder_name=folder_name,
                chapter=chapter,
                page=doc.metadata.get("page", ""),
                text=text[:max_chars],
            )
        )
        counter += 1
        if len(snippets) >= max_snippets:
            break

    return snippets

