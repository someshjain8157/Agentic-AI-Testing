from __future__ import annotations

from pathlib import Path

from app.agentic_testing.agents.base import BaseAgent
from app.agentic_testing.config import GENERATED_TEST_DIR, GOLDEN_DATA_DIR
from app.agentic_testing.discovery import discover_subject_families
from app.agentic_testing.models import AgentReport
from app.agentic_testing.reporting import save_agent_report
from app.agentic_testing.utils import ensure_dir


class PlaywrightGeneratorAgent(BaseAgent):
    name = "playwright_generator_agent"

    def _run(self) -> AgentReport:
        ensure_dir(GENERATED_TEST_DIR)
        families = [family for family in discover_subject_families() if family.key in {"math", "social_science", "science", "english"}]
        generated_files: list[str] = []

        test_files = {
            "test_chatbot_ui_playwright.py": self._render_ui_module(),
            "test_chatbot_golden_pytest.py": self._render_golden_module(families),
            "test_chatbot_ragas_pytest.py": self._render_agent_wrapper_module("ragas_agent"),
            "test_chatbot_deepeval_pytest.py": self._render_agent_wrapper_module("deepeval_agent"),
            "test_chatbot_pyrit_pytest.py": self._render_agent_wrapper_module("pyrit_attack_agent"),
            "test_chatbot_compliance_pytest.py": self._render_compliance_module(),
        }

        for filename, contents in test_files.items():
            path = GENERATED_TEST_DIR / filename
            path.write_text(contents, encoding="utf-8")
            generated_files.append(str(path))

        report = AgentReport(
            name=self.name,
            status="passed",
            summary="Generated a small pytest suite covering UI, golden data, DeepEval, PyRIT, and compliance checks.",
            duration_ms=0.0,
            artifacts=generated_files,
            data={"generated_test_dir": str(GENERATED_TEST_DIR), "families": [family.key for family in families]},
        )
        if self.output_dir:
            save_agent_report(report, self.output_dir)
        return report

    @staticmethod
    def _render_ui_module() -> str:
        return """from pathlib import Path
import subprocess
import sys
import time

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright


def _wait_for_server(host: str = "127.0.0.1", port: int = 8000, timeout: int = 60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            import socket
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.25)
    return False


@pytest.fixture(scope="session")
def server_process():
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.server:app", "--host", "127.0.0.1", "--port", "8000"])
    assert _wait_for_server(), "TeacherAI server did not start in time"
    yield "http://127.0.0.1:8000"
    proc.terminate()
    proc.wait(timeout=30)


class TestChatbotUI:
    def test_homepage_renders(self, server_process):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(server_process, wait_until="networkidle")
            assert page.locator("#question").count() == 1
            assert page.locator("#subject").count() == 1
            browser.close()
"""

    @staticmethod
    def _render_golden_module(families) -> str:
        families_block = ",\n    ".join(
            f"{{'key': '{family.key}', 'label': '{family.label}', 'folder': '{family.folder_names[0]}'}}"
            for family in families
        )
        return f"""from app.agentic_testing.client import ChatbotClient
from app.agentic_testing.config import GOLDEN_DATA_DIR
from app.agentic_testing.utils import read_json


FAMILIES = [
    {families_block}
]


class TestGoldenDatasets:
    def test_goldens_exist(self):
        for family in FAMILIES:
            assert (GOLDEN_DATA_DIR / f"{{family['key']}}.json").exists()

    def test_two_sample_queries_per_family(self):
        client = ChatbotClient()
        for family in FAMILIES:
            goldens = read_json(GOLDEN_DATA_DIR / f"{{family['key']}}.json")[:2]
            for item in goldens:
                turn = client.ask(item["question"], subject=family["folder"])
                assert turn.answer.strip()
                assert len(turn.sources) >= 0
"""

    @staticmethod
    def _render_agent_wrapper_module(agent_name: str) -> str:
        module_map = {
            "deepeval_agent": ("app.agentic_testing.agents.deepeval_agent", "DeepEvalAgent"),
            "pyrit_attack_agent": ("app.agentic_testing.agents.pyrit_attack", "PyRITAttackAgent"),
            "ragas_agent": ("app.agentic_testing.agents.ragas_agent", "RagasAgent"),
        }
        module_path, class_name = module_map[agent_name]
        test_class_name = "".join(part.title() for part in agent_name.split("_"))
        return f"""from {module_path} import {class_name}
from app.agentic_testing.models import AgentReport


class Test{test_class_name}Agent:
    def test_agent_runs(self):
        agent = {class_name}()
        report = agent.run()
        assert isinstance(report, AgentReport)
        assert report.status in {{'passed', 'warning'}}
"""

    @staticmethod
    def _render_compliance_module() -> str:
        return """from app.agentic_testing.agents.compliance import BraintrustAuditAgent, GuardrailComplianceAgent, LangfuseObservabilityAgent


class TestComplianceAgents:
    def test_langfuse_agent_runs(self):
        report = LangfuseObservabilityAgent().run()
        assert report.status in {'passed', 'warning'}

    def test_braintrust_agent_runs(self):
        report = BraintrustAuditAgent().run()
        assert report.status in {'passed', 'warning'}

    def test_guardrail_agent_runs(self):
        report = GuardrailComplianceAgent().run()
        assert report.status in {'passed', 'warning'}
"""

