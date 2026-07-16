from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.agentic_testing.agents.base import BaseAgent
from app.agentic_testing.agents.compliance import BraintrustAuditAgent, GuardrailComplianceAgent, LangfuseObservabilityAgent
from app.agentic_testing.agents.deepeval_agent import DeepEvalAgent
from app.agentic_testing.agents.golden_dataset import GoldenDatasetAgent
from app.agentic_testing.agents.ragas_agent import RagasAgent
from app.agentic_testing.agents.playwright_generator import PlaywrightGeneratorAgent
from app.agentic_testing.agents.playwright_runner import PlaywrightRunnerAgent
from app.agentic_testing.agents.pyrit_attack import PyRITAttackAgent
from app.agentic_testing.config import ARTIFACT_DIR
from app.agentic_testing.models import RunReport
from app.agentic_testing.reporting import save_run_report
from app.agentic_testing.utils import ensure_dir


class TestingOrchestrator:
    def __init__(self, output_dir: Path | None = None, *, regenerate_playwright_tests: bool = False):
        self.output_dir = output_dir or ARTIFACT_DIR
        self.regenerate_playwright_tests = regenerate_playwright_tests
        ensure_dir(self.output_dir)

        self.agents: list[BaseAgent] = [
            GoldenDatasetAgent(output_dir=self.output_dir),
            RagasAgent(output_dir=self.output_dir),
            DeepEvalAgent(output_dir=self.output_dir),
            PyRITAttackAgent(output_dir=self.output_dir),
            LangfuseObservabilityAgent(output_dir=self.output_dir),
            BraintrustAuditAgent(output_dir=self.output_dir),
            GuardrailComplianceAgent(output_dir=self.output_dir),
            PlaywrightGeneratorAgent(output_dir=self.output_dir, regenerate=self.regenerate_playwright_tests),
            PlaywrightRunnerAgent(output_dir=self.output_dir),
        ]

    def run(self) -> RunReport:
        run_report = RunReport(root_dir=self.output_dir)
        for agent in self.agents:
            report = agent.run()
            run_report.agents.append(report)
        run_report.finalize()
        save_run_report(run_report, self.output_dir)
        return run_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the TeacherAI agentic test framework sequentially.")
    parser.add_argument("--output-dir", default=str(ARTIFACT_DIR), help="Where to write reports and generated artifacts.")
    parser.add_argument(
        "--regenerate-playwright-tests",
        action="store_true",
        help="Regenerate the generated Playwright pytest files before running the suite.",
    )
    args = parser.parse_args()

    orchestrator = TestingOrchestrator(
        output_dir=Path(args.output_dir),
        regenerate_playwright_tests=args.regenerate_playwright_tests,
    )
    report = orchestrator.run()
    print(json.dumps(report.to_dict(), indent=2, ensure_ascii=True))
    return 0 if report.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

