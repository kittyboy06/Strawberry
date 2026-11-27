import hashlib
import tempfile
from pathlib import Path
import pytest

from strawberry_cli.pro.app import StrawberryProApp
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.services.cache import CacheService
from strawberry_cli.services.pro_state import ProStateService


def _seed_test_catalog(repo: SQLiteCatalogRepository, filename: str, sha: str) -> None:
    with repo._get_connection() as conn:
        conn.execute("INSERT INTO years (id, year_number, display_name) VALUES ('y2', 2, '2nd Year')")
        conn.execute("INSERT INTO years (id, year_number, display_name) VALUES ('y3', 3, '3rd Year')")
        conn.execute(
            "INSERT INTO semesters (id, year_id, semester_number, display_name) VALUES ('s3', 'y2', 3, 'Semester 3')"
        )
        conn.execute(
            "INSERT INTO semesters (id, year_id, semester_number, display_name) VALUES ('s5', 'y3', 5, 'Semester 5')"
        )
        conn.execute(
            "INSERT INTO subjects (id, semester_id, subject_code, subject_name, is_active) VALUES ('sub2', 's3', 'CS101', 'Alpha Course', 1)"
        )
        conn.execute(
            "INSERT INTO subjects (id, semester_id, subject_code, subject_name, is_active) VALUES ('sub3', 's5', 'CS201', 'Beta Course', 1)"
        )
        conn.execute(
            "INSERT INTO experiments (id, subject_id, experiment_number, title, description, is_published) VALUES ('exp2', 'sub2', 1, 'Alpha Program', 'Alpha test', 1)"
        )
        conn.execute(
            "INSERT INTO experiment_versions (id, experiment_id, version_number, storage_path, filename, sha256) VALUES ('ver2', 'exp2', 1, 'programs/exp2/alpha.py', ?, ?)",
            (filename, sha),
        )
        conn.commit()


@pytest.mark.anyio
async def test_strawberry_pro_app_mount_bookmarks_history_and_search(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp = Path(temp_dir)
        repo = SQLiteCatalogRepository(db_path=tmp / "test_pro.db")
        cache = CacheService(cache_dir=tmp / "cache")
        state = ProStateService(state_path=tmp / "pro_state.json")

        filename = "alpha.py"
        raw_code = b"print('alpha')\n"
        sha = hashlib.sha256(raw_code).hexdigest()
        _seed_test_catalog(repo, filename, sha)
        cache.save_file(filename, raw_code, sha)

        copied_payloads: list[str] = []
        monkeypatch.setattr(
            "strawberry_cli.pro.app.clipboard_service.copy_to_clipboard",
            lambda text: copied_payloads.append(text) or True,
        )

        app = StrawberryProApp(repository=repo, state_service=state, cache=cache)

        async with app.run_test() as pilot:
            assert app.query_one("#header-title") is not None
            assert app.query_one("#subjects-list") is not None
            assert app.query_one("#experiments-list") is not None
            assert app.query_one("#code-viewer") is not None

            assert app.selected_year_number == 2
            assert app.selected_subject is not None
            assert app.selected_experiment is not None

            exp_id = app.selected_experiment.id
            await pilot.press("b")
            assert state.is_bookmarked(exp_id)

            await pilot.press("c")
            assert len(copied_payloads) == 1
            assert len(state.get_history()) == 1
            assert state.get_history()[0]["experiment_id"] == exp_id

            await pilot.click("#btn-mode-bookmarks")
            assert app.view_mode == "bookmarks"
            assert any(e.id == exp_id for e in app.experiments)

            await pilot.click("#btn-mode-recent")
            assert app.view_mode == "recent"
            assert any(e.id == exp_id for e in app.experiments)

            await pilot.click("#btn-year-3")
            assert app.view_mode == "all"
            assert app.selected_year_number == 3

            await pilot.click("#btn-year-2")
            search_input = app.query_one("#search-input")
            search_input.value = "Alpha Program"
            assert app.selected_experiment is not None
            assert app.selected_experiment.title == "Alpha Program"

            search_input.value = ""
            await pilot.click("#btn-year-2")
            cache.get_file_path(filename).write_text("# TAMPERED", encoding="utf-8")
            app.action_copy_code()
            assert len(copied_payloads) == 1

            app.reset_inactivity()
            assert app.inactivity_seconds == 7


def test_pro_state_history_cap():
    with tempfile.TemporaryDirectory() as temp_dir:
        svc = ProStateService(state_path=Path(temp_dir) / "pro_state.json", max_history=3)
        for i in range(5):
            svc.record_history(f"exp-{i}", f"Program {i}", "CS101", f"f{i}.py")

        hist = svc.get_history()
        assert len(hist) == 3
        assert [h["experiment_id"] for h in hist] == ["exp-4", "exp-3", "exp-2"]
