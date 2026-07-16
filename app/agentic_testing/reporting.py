from __future__ import annotations

from pathlib import Path
from typing import Any

from app.agentic_testing.models import AgentReport, RunReport
from app.agentic_testing.utils import ensure_dir, write_json


def save_agent_report(report: AgentReport, output_dir: Path) -> Path:
    ensure_dir(output_dir)
    path = output_dir / f"{report.name}.json"
    return write_json(path, report.to_dict())


def save_run_report(report: RunReport, output_dir: Path) -> Path:
    ensure_dir(output_dir)
    path = output_dir / f"run_{report.id}.json"
    return write_json(path, report.to_dict())

