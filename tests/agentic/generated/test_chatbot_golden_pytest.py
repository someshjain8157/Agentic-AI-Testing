from app.agentic_testing.client import ChatbotClient
from app.agentic_testing.config import GOLDEN_DATA_DIR
from app.agentic_testing.utils import read_json


FAMILIES = [
    {'key': 'english', 'label': 'English', 'folder': 'ENGLISH- Kaveri'},
    {'key': 'math', 'label': 'Math', 'folder': 'MATH - Ganita Manjari'},
    {'key': 'science', 'label': 'Science', 'folder': 'SCIENCE - Exploration'},
    {'key': 'social_science', 'label': 'Social Science', 'folder': 'SOCIAL SCIENCE - Understanding Society India and Beyond'}
]


class TestGoldenDatasets:
    def test_goldens_exist(self):
        for family in FAMILIES:
            assert (GOLDEN_DATA_DIR / f"{family['key']}.json").exists()

    def test_two_sample_queries_per_family(self):
        client = ChatbotClient()
        for family in FAMILIES:
            goldens = read_json(GOLDEN_DATA_DIR / f"{family['key']}.json")[:2]
            for item in goldens:
                turn = client.ask(item["question"], subject=family["folder"])
                assert turn.answer.strip()
                assert len(turn.sources) >= 0
