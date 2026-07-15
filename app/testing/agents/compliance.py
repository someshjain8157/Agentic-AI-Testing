from __future__ import annotations

import json
from pathlib import Path

from app.testing.agents.base import BaseAgent
from app.testing.config import ARTIFACT_DIR
from app.testing.models import AgentReport
from app.testing.reporting import save_agent_report
from app.testing.utils import ensure_dir, read_json, write_json


class LangfuseObservabilityAgent(BaseAgent):
    name = "langfuse_observability_agent"

    def _run(self) -> AgentReport:
        logs = _read_jsonl(Path("logs") / "agent.jsonl")
        coverage = _basic_log_coverage(logs, required_fields={"request_id", "event"})
        data = {"integration": "langfuse", "coverage": coverage, "log_count": len(logs)}
        report = AgentReport(name=self.name, status="passed", summary="Langfuse-style observability review completed.", duration_ms=0.0, data=data)
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report


class BraintrustAuditAgent(BaseAgent):
    name = "braintrust_audit_agent"

    def _run(self) -> AgentReport:
        logs = _read_jsonl(Path("logs") / "audit.jsonl")
        coverage = _basic_log_coverage(logs, required_fields={"request_id", "question", "answer", "citations"})
        data = {"integration": "braintrust", "coverage": coverage, "audit_count": len(logs)}
        report = AgentReport(name=self.name, status="passed", summary="Braintrust-style audit review completed.", duration_ms=0.0, data=data)
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report


class GuardrailComplianceAgent(BaseAgent):
    name = "guardrail_compliance_agent"

    def _run(self) -> AgentReport:
        logs = _read_jsonl(Path("logs") / "audit.jsonl")
        findings = []
        for row in logs:
            if _looks_like_pii(row.get("question", "")):
                findings.append({"type": "question_pii", "request_id": row.get("request_id")})
            if _looks_like_pii(row.get("answer", "")):
                findings.append({"type": "answer_pii", "request_id": row.get("request_id")})
            if not row.get("citations"):
                findings.append({"type": "missing_citations", "request_id": row.get("request_id")})

        report = AgentReport(
            name=self.name,
            status="passed" if not findings else "warning",
            summary="Guardrail policy checks completed.",
            duration_ms=0.0,
            data={"integration": "guardrails_ai", "findings": findings, "log_count": len(logs)},
        )
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _basic_log_coverage(rows: list[dict], required_fields: set[str]) -> float:
    if not rows:
        return 0.0
    covered = 0
    for row in rows:
        if required_fields.issubset(set(row.keys())):
            covered += 1
    return round(covered / len(rows), 3)


def _looks_like_pii(text: str) -> bool:
    lowered = text.lower()
    return "@" in lowered or any(char.isdigit() for char in lowered) and len(lowered) > 10

