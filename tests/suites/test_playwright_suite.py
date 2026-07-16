from __future__ import annotations

from pathlib import Path

from app.agentic_testing.agents.playwright_generator import PlaywrightGeneratorAgent
from app.agentic_testing.config import GENERATED_TEST_DIR


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
        PlaywrightGeneratorAgent(regenerate=True).run()


def test_playwright_generator_reuses_existing_files():
    _ensure_generated_files_exist()
    before = {path: path.stat().st_mtime_ns for path in _generated_paths() if path.exists()}

    report = PlaywrightGeneratorAgent().run()

    assert report.status == "passed"
    assert report.data["regenerated"] is False
    assert all(path.exists() for path in _generated_paths())

    after = {path: path.stat().st_mtime_ns for path in _generated_paths() if path.exists()}
    assert before == after


def test_playwright_generator_can_regenerate_when_requested():
    _ensure_generated_files_exist()
    report = PlaywrightGeneratorAgent(regenerate=True).run()

    assert report.status == "passed"
    assert report.data["regenerated"] is True
    assert all(path.exists() for path in _generated_paths())
