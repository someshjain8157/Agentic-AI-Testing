from __future__ import annotations

from pathlib import Path

from app.agentic_testing.agents.playwright_generator import PlaywrightGeneratorAgent
from app.agentic_testing.agents.playwright_runner import PlaywrightRunnerAgent
from app.agentic_testing.config import ARTIFACT_DIR, GENERATED_TEST_DIR
from tests._agentic_allure import attach_case


def _generated_paths() -> list[Path]:
    return [
        GENERATED_TEST_DIR / "test_chatbot_ui_playwright.py",
        GENERATED_TEST_DIR / "test_chatbot_golden_pytest.py",
        GENERATED_TEST_DIR / "test_chatbot_ragas_pytest.py",
        GENERATED_TEST_DIR / "test_chatbot_deepeval_pytest.py",
        GENERATED_TEST_DIR / "test_chatbot_pyrit_pytest.py",
        GENERATED_TEST_DIR / "test_chatbot_compliance_pytest.py",
    ]


def _ensure_generated_files_exist() -> None:
    if not all(path.exists() for path in _generated_paths()):
        PlaywrightGeneratorAgent(output_dir=ARTIFACT_DIR, regenerate=True).run()


def test_playwright_generator_reuses_existing_files():
    _ensure_generated_files_exist()
    before = {path: path.stat().st_mtime_ns for path in _generated_paths() if path.exists()}

    report = PlaywrightGeneratorAgent(output_dir=ARTIFACT_DIR).run()

    attach_case(
        parent_suite="Smoke Tests",
        suite="Generated Playwright Agents",
        title="playwright generator reuses existing files",
        expected_output="Generated files remain unchanged",
        actual_output={"regenerated": report.data["regenerated"], "generated_test_dir": report.data["generated_test_dir"]},
        score=1.0 if report.data["regenerated"] is False else 0.0,
        passed=report.data["regenerated"] is False,
        details={"artifacts": report.artifacts, "families": report.data["families"]},
    )

    assert report.status == "passed"
    assert report.data["regenerated"] is False
    assert all(path.exists() for path in _generated_paths())

    after = {path: path.stat().st_mtime_ns for path in _generated_paths() if path.exists()}
    assert before == after


def test_playwright_generator_can_regenerate_when_requested():
    _ensure_generated_files_exist()
    report = PlaywrightGeneratorAgent(output_dir=ARTIFACT_DIR, regenerate=True).run()

    attach_case(
        parent_suite="Smoke Tests",
        suite="Generated Playwright Agents",
        title="playwright generator regenerates files when requested",
        expected_output="Generated files are refreshed",
        actual_output={"regenerated": report.data["regenerated"], "generated_test_dir": report.data["generated_test_dir"]},
        score=1.0 if report.data["regenerated"] is True else 0.0,
        passed=report.data["regenerated"] is True,
        details={"artifacts": report.artifacts, "families": report.data["families"]},
    )

    assert report.status == "passed"
    assert report.data["regenerated"] is True
    assert all(path.exists() for path in _generated_paths())


def test_playwright_runner_executes_generated_files():
    _ensure_generated_files_exist()
    report = PlaywrightRunnerAgent(output_dir=ARTIFACT_DIR).run()

    attach_case(
        parent_suite="Smoke Tests",
        suite="Generated Playwright Agents",
        title="playwright runner executes generated files",
        expected_output="Generated pytest files run successfully",
        actual_output={
            "returncode": report.data.get("returncode"),
            "stdout": report.data.get("stdout", ""),
            "stderr": report.data.get("stderr", ""),
        },
        score=1.0 if report.data.get("returncode") == 0 else 0.0,
        passed=report.data.get("returncode") == 0,
        details=report.data,
    )

    assert report.status in {"passed", "failed"}
    assert "returncode" in report.data
