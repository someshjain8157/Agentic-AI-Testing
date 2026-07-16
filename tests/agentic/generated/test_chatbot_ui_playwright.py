from pathlib import Path
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
