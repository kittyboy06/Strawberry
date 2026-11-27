import hashlib
import tempfile
from pathlib import Path
from strawberry_cli.lite.workflow import LiteWorkflow
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.core.input_handler import TimedInputHandler
from strawberry_cli.services.cache import CacheService


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

        filename = "hello_lab.py"
        raw_code = b"print('ok')\n"
        sha = hashlib.sha256(raw_code).hexdigest()

        test_cache = CacheService(cache_dir=cache_dir)
        test_cache.save_file(filename, raw_code, sha)

        repo = SQLiteCatalogRepository(db_path=db_path)
        with repo._get_connection() as conn:
            conn.execute("INSERT INTO years (id, year_number, display_name) VALUES ('y2', 2, '2nd Year')")
            conn.execute(
                "INSERT INTO semesters (id, year_id, semester_number, display_name) VALUES ('s3', 'y2', 3, 'Semester 3')"
            )
            conn.execute(
                "INSERT INTO subjects (id, semester_id, subject_code, subject_name, is_active) VALUES ('sub1', 's3', 'CS101', 'Sample Course', 1)"
            )
            conn.execute(
                "INSERT INTO experiments (id, subject_id, experiment_number, title, description, is_published) VALUES ('exp1', 'sub1', 1, 'Hello Lab', 'Sample test', 1)"
            )
            conn.execute(
                "INSERT INTO experiment_versions (id, experiment_id, version_number, storage_path, filename, sha256) VALUES ('ver1', 'exp1', 1, 'programs/exp1/hello_lab.py', ?, ?)",
                (filename, sha),
            )
            conn.commit()

        mock_input = MockInputHandler(responses=["1", "1", "1"])
        workflow = LiteWorkflow(repository=repo, input_handler=mock_input)

        monkeypatch.setattr("strawberry_cli.lite.workflow.cache_service", test_cache)
        monkeypatch.setattr("strawberry_cli.lite.workflow.clipboard_service.copy_to_clipboard", lambda _t: True)

        workflow.run()

        captured = capsys.readouterr().out
        assert "Welcome to Strawberry!" in captured
        assert "Sample Course" in captured
        assert "Program retrieved" in captured
        assert "Integrity verified (SHA-256)" in captured
