from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SubjectFamily:
    key: str
    label: str
    folder_names: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Snippet:
    snippet_id: str
    subject_key: str
    folder_name: str
    chapter: str
    page: int | str
    text: str

    def citation(self) -> dict[str, Any]:
        return {
            "subject": self.folder_name,
            "chapter": self.chapter,
            "page": self.page,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GoldenExample:
    id: str
    subject_key: str
    subject_label: str
    question: str
    expected_answer: str
    citations: list[dict[str, Any]]
    source_ids: list[str] = field(default_factory=list)
    difficulty: str = "medium"
    task_type: str = "short_answer"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentReport:
    name: str
    status: str
    summary: str
    duration_ms: float
    artifacts: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid4().hex)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["artifacts"] = [str(item) for item in self.artifacts]
        return payload


@dataclass
class RunReport:
    id: str = field(default_factory=lambda: uuid4().hex)
    started_at: str = field(default_factory=utc_now)
    finished_at: str | None = None
    agents: list[AgentReport] = field(default_factory=list)
    status: str = "running"
    root_dir: Path | None = None

    def finalize(self) -> None:
        self.finished_at = utc_now()
        self.status = "passed" if all(agent.status == "passed" for agent in self.agents) else "partial"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "agents": [agent.to_dict() for agent in self.agents],
            "root_dir": str(self.root_dir) if self.root_dir else None,
        }

