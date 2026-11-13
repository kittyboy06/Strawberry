import tempfile
from pathlib import Path
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.services.cache import CacheService


def test_sqlite_repository_initialization_and_seed():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_catalog.db"
        repo = SQLiteCatalogRepository(db_path=db_path)

        # Test years
        years = repo.get_years()
        assert len(years) == 3
        assert [y.year_number for y in years] == [2, 3, 4]

        # Test subjects for 2nd Year (combining Semester 3 and 4)
        subjects = repo.get_subjects_by_year(2)
        assert len(subjects) >= 4
        assert any(s.subject_name == "Computer Networks" for s in subjects)

        # Test experiments for Computer Networks
        cn_sub = next(s for s in subjects if s.subject_name == "Computer Networks")
        experiments = repo.get_experiments_by_subject(cn_sub.id)
        assert len(experiments) >= 2
        assert any(e.title == "Socket Programming" for e in experiments)

        # Test version lookup
        exp = experiments[0]
        version = repo.get_latest_version(exp.id)
        assert version is not None
        assert version.filename == "socket_server.py"
        assert len(version.sha256) == 64


def test_cache_service():
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir) / "cache"
        cache = CacheService(cache_dir=cache_dir)

        content = b"print('Hello Strawberry!')\n"
        import hashlib

        expected_hash = hashlib.sha256(content).hexdigest()

        # Save and verify
        saved_file = cache.save_file("hello.py", content, expected_hash)
        assert saved_file.exists()
        assert cache.is_cached("hello.py")
        assert cache.verify_integrity("hello.py", expected_hash)
        assert cache.read_source_code("hello.py") == "print('Hello Strawberry!')\n"
