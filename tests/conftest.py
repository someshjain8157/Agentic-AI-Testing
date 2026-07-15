import os
from pathlib import Path


def pytest_configure(config):
    output_dir = Path("reports/allure")
    output_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("ALLURE_DIR", str(output_dir))
