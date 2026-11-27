"""Tests for transactional Supabase sync pruning, orphan cache cleanup, and failure guards."""

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.repository.supabase_sync import SupabaseSyncService
from strawberry_cli.services.cache import CacheService


def _mock_response(status_code: int, json_data=None, content: bytes = b""):
    res = MagicMock()
    res.status_code = status_code
    res.json.return_value = json_data
    res.content = content
    return res


def _seed_stale_records(repo: SQLiteCatalogRepository) -> None:
    with repo._get_connection() as conn:
        conn.execute("INSERT INTO years (id, year_number, display_name) VALUES ('y_old', 2, 'Old Year')")
        conn.execute(
            "INSERT INTO semesters (id, year_id, semester_number, display_name) VALUES ('s_old', 'y_old', 3, 'Old Sem')"
        )
        conn.execute(
            "INSERT INTO subjects (id, semester_id, subject_code, subject_name, is_active) VALUES ('sub_old', 's_old', 'OLD1', 'Stale Subject', 1)"
        )
        conn.commit()


def test_sync_prunes_stale_rows_and_orphans(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        repo = SQLiteCatalogRepository(db_path=tmp_path / "catalog.db")
        _seed_stale_records(repo)
        cache = CacheService(cache_dir=tmp_path / "cache")

        (cache.cache_dir / "old_file.py").write_text("# stale", encoding="utf-8")

        live_code = b"SELECT 1;\n"
        live_sha = hashlib.sha256(live_code).hexdigest()

        responses = {
            "/rest/v1/years?select=*": _mock_response(
                200, [{"id": "y2", "year_number": 2, "display_name": "2nd Year"}]
            ),
            "/rest/v1/semesters?select=*": _mock_response(
                200, [{"id": "s4", "year_id": "y2", "semester_number": 4, "display_name": "Semester 4"}]
            ),
            "/rest/v1/subjects?select=*&is_active=eq.true": _mock_response(
                200,
                [
                    {
                        "id": "sub1",
                        "semester_id": "s4",
                        "subject_code": "CS401",
                        "subject_name": "Relational Databases",
                        "is_active": True,
                    }
                ],
            ),
            "/rest/v1/experiments?select=*&is_published=eq.true": _mock_response(
                200,
                [
                    {
                        "id": "exp1",
                        "subject_id": "sub1",
                        "experiment_number": 1,
                        "title": "Customer Schema",
                        "description": "Live DB exp",
                        "is_published": True,
                    }
                ],
            ),
            "/rest/v1/experiment_versions?select=*": _mock_response(
                200,
                [
                    {
                        "id": "ver1",
                        "experiment_id": "exp1",
                        "version_number": 1,
                        "storage_path": "programs/exp1/s1.sql",
                        "filename": "s1.sql",
                        "sha256": live_sha,
                    }
                ],
            ),
            "/storage/v1/object/public/programs/programs/exp1/s1.sql": _mock_response(
                200, content=live_code
            ),
        }

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = False

        def fake_get(url, headers=None):
            for suffix, resp in responses.items():
                if url.endswith(suffix):
                    return resp
            return _mock_response(404)

        mock_client.get.side_effect = fake_get
        monkeypatch.setattr("strawberry_cli.repository.supabase_sync.httpx.Client", lambda **kw: mock_client)

        sync_svc = SupabaseSyncService(repo=repo, cache=cache)
        monkeypatch.setattr(sync_svc, "is_online", lambda: True)
        monkeypatch.setattr("strawberry_cli.core.config.config.local_app_data", tmp_path)

        result = sync_svc.sync()
        assert result["synced"] is True
        assert result["files_downloaded"] == 1
        assert result["files_pruned"] == 1

        assert len(repo.get_years()) == 1
        subs = repo.get_subjects_by_year(2)
        assert [s.subject_code for s in subs] == ["CS401"]
        exps = repo.get_experiments_by_subject("sub1")
        assert [e.title for e in exps] == ["Customer Schema"]
        assert cache.is_cached("s1.sql")
        assert not (cache.cache_dir / "old_file.py").exists()


def test_sync_aborts_without_wiping_on_partial_http_error(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        repo = SQLiteCatalogRepository(db_path=tmp_path / "catalog.db")
        _seed_stale_records(repo)
        cache = CacheService(cache_dir=tmp_path / "cache")
        before_subs = repo.get_subjects_by_year(2)
        assert len(before_subs) == 1

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = False
        mock_client.get.side_effect = lambda url, headers=None: (
            _mock_response(500) if "subjects" in url else _mock_response(200, [])
        )
        monkeypatch.setattr("strawberry_cli.repository.supabase_sync.httpx.Client", lambda **kw: mock_client)

        sync_svc = SupabaseSyncService(repo=repo, cache=cache)
        monkeypatch.setattr(sync_svc, "is_online", lambda: True)

        result = sync_svc.sync()
        assert result["synced"] is False
        assert len(repo.get_subjects_by_year(2)) == 1


def test_fresh_repo_starts_empty():
    with tempfile.TemporaryDirectory() as tmp:
        repo = SQLiteCatalogRepository(db_path=Path(tmp) / "clean.db")
        assert repo.get_years() == []
