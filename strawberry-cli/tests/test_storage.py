import hashlib
import tempfile
from pathlib import Path
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.services.cache import CacheService


def test_sqlite_repository_queries():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_catalog.db"
        repo = SQLiteCatalogRepository(db_path=db_path)

        sample_code = b"print('sample')\n"
        sample_sha = hashlib.sha256(sample_code).hexdigest()

        with repo._get_connection() as conn:
            conn.execute("INSERT INTO years (id, year_number, display_name) VALUES ('y2', 2, '2nd Year')")
            conn.execute("INSERT INTO years (id, year_number, display_name) VALUES ('y3', 3, '3rd Year')")
            conn.execute(
                "INSERT INTO semesters (id, year_id, semester_number, display_name) VALUES ('s3', 'y2', 3, 'Semester 3')"
            )
            conn.execute(
                "INSERT INTO subjects (id, semester_id, subject_code, subject_name, is_active) VALUES ('sub1', 's3', 'CS101', 'Sample Subject', 1)"
            )
            conn.execute(
                "INSERT INTO experiments (id, subject_id, experiment_number, title, description, is_published) VALUES ('exp1', 'sub1', 1, 'Sample Program', 'Desc', 1)"
            )
            conn.execute(
                "INSERT INTO experiment_versions (id, experiment_id, version_number, storage_path, filename, sha256) VALUES ('ver1', 'exp1', 1, 'programs/exp1/sample.py', 'sample.py', ?)",
                (sample_sha,),
            )
            conn.commit()

        years = repo.get_years()
        assert [y.year_number for y in years] == [2, 3]

        subjects = repo.get_subjects_by_year(2)
        assert len(subjects) == 1
        assert subjects[0].subject_code == "CS101"

        experiments = repo.get_experiments_by_subject("sub1")
        assert len(experiments) == 1
        assert experiments[0].title == "Sample Program"

        version = repo.get_latest_version("exp1")
        assert version is not None
        assert version.filename == "sample.py"
        assert version.sha256 == sample_sha


def test_cache_service():
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir) / "cache"
        cache = CacheService(cache_dir=cache_dir)

        content = b"print('Hello Strawberry!')\n"
        expected_hash = hashlib.sha256(content).hexdigest()

        saved_file = cache.save_file("hello.py", content, expected_hash)
        assert saved_file.exists()
        assert cache.is_cached("hello.py")
        assert cache.verify_integrity("hello.py", expected_hash)
        assert cache.read_source_code("hello.py") == "print('Hello Strawberry!')\n"
