import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_configure(config):
    output_dir = Path("reports/allure")
    output_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("ALLURE_DIR", str(output_dir))
