from pathlib import Path

from app.config import PROJECT_ROOT, OLLAMA_MODEL

TESTING_ROOT = PROJECT_ROOT / "tests" / "agentic"
GOLDEN_DATA_DIR = TESTING_ROOT / "golden"
GENERATED_TEST_DIR = TESTING_ROOT / "generated"
ARTIFACT_DIR = PROJECT_ROOT / "reports" / "agentic"

DEFAULT_GOLDEN_PER_SUBJECT = 10
DEFAULT_DEEPEVAL_SAMPLES = 2
DEFAULT_PYRIT_QUERIES = 10
DEFAULT_CONTEXT_SNIPPETS = 6
DEFAULT_MODEL = OLLAMA_MODEL

CANONICAL_SUBJECTS = {
    "math": "Math",
    "social_science": "Social Science",
    "science": "Science",
    "english": "English",
}

