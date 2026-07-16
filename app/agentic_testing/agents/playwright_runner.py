from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.agentic_testing.agents.base import BaseAgent
from app.agentic_testing.config import GENERATED_TEST_DIR
from app.agentic_testing.models import AgentReport
from app.agentic_testing.reporting import save_agent_report


class PlaywrightRunnerAgent(BaseAgent):
    name = "playwright_runner_agent"

    def _run(self) -> AgentReport:
        if not GENERATED_TEST_DIR.exists():
            return AgentReport(
                name=self.name,
                status="warning",
                summary="No generated Playwright tests found.",
                duration_ms=0.0,
                data={"generated_test_dir": str(GENERATED_TEST_DIR)},
            )

        test_files = sorted(GENERATED_TEST_DIR.glob("test_*.py"))
        if not test_files:
            return AgentReport(
                name=self.name,
                status="warning",
                summary="No generated Playwright files matched the expected pattern.",
                duration_ms=0.0,
                data={"generated_test_dir": str(GENERATED_TEST_DIR)},
            )

        cmd = [sys.executable, "-m", "pytest", "-q", *[str(path) for path in test_files]]
        process = subprocess.run(cmd, capture_output=True, text=True)
        status = "passed" if process.returncode == 0 else "failed"
        report = AgentReport(
            name=self.name,
            status=status,
            summary="Playwright tests executed.",
            duration_ms=0.0,
            data={"returncode": process.returncode, "stdout": process.stdout[-2000:], "stderr": process.stderr[-2000:]},
        )
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report
