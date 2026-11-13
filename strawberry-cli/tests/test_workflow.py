import tempfile
from pathlib import Path
from strawberry_cli.lite.workflow import LiteWorkflow
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.core.input_handler import TimedInputHandler
from strawberry_cli.services.cache import CacheService
from strawberry_cli.repository.mock_data import DEMO_PROGRAMS, get_demo_hash


class MockInputHandler(TimedInputHandler):
    """Simulates user input choices for automated testing."""

    def __init__(self, responses: list[str]):
        super().__init__()
        self.responses = list(responses)

    def get_input(self, prompt: str, validator=None, error_message: str = "", timeout_seconds=None) -> str:
        if not self.responses:
            raise RuntimeError("Ran out of mock responses")
        val = self.responses.pop(0)
        if validator and not validator(val):
            raise ValueError(f"Mock response '{val}' rejected by validator")
        return val


def test_end_to_end_lite_workflow(capsys, monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        db_path = temp_path / "catalog.db"
        cache_dir = temp_path / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Seed program file in test cache
        filename = "socket_server.py"
        test_cache = CacheService(cache_dir=cache_dir)
        test_cache.save_file(
            filename,
            DEMO_PROGRAMS[filename].encode("utf-8"),
            get_demo_hash(filename),
        )

        repo = SQLiteCatalogRepository(db_path=db_path)

        # Simulate student choosing:
        # 1 -> 2nd Year
        # 1 -> Computer Networks
        # 1 -> Socket Programming
        mock_input = MockInputHandler(responses=["1", "1", "1"])
        workflow = LiteWorkflow(repository=repo, input_handler=mock_input)

        # Patch global cache service to test cache
        monkeypatch.setattr("strawberry_cli.lite.workflow.cache_service", test_cache)

        workflow.run()

        captured = capsys.readouterr().out
        assert "Welcome to Strawberry!" in captured
        assert "Computer Networks" in captured
        assert "Program retrieved" in captured
        assert "Integrity verified (SHA-256)" in captured
