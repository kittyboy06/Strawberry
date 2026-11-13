"""SQLite local repository implementation for offline-first catalog access."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional
from strawberry_cli.core.config import config
from strawberry_cli.models import Year, Semester, Subject, Experiment, ExperimentVersion
from .base import BaseCatalogRepository
from .mock_data import (
    SEED_YEARS,
    SEED_SEMESTERS,
    SEED_SUBJECTS,
    SEED_EXPERIMENTS,
    DEMO_PROGRAMS,
    get_demo_hash,
)


class SQLiteCatalogRepository(BaseCatalogRepository):
    """Manages the local SQLite database at %LOCALAPPDATA%\\Strawberry\\catalog.db."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.database_path
        self._init_database()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Create tables if they do not exist and seed default demonstration catalog."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS years (
                    id TEXT PRIMARY KEY,
                    year_number INTEGER NOT NULL UNIQUE,
                    display_name TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS semesters (
                    id TEXT PRIMARY KEY,
                    year_id TEXT NOT NULL,
                    semester_number INTEGER NOT NULL,
                    display_name TEXT NOT NULL,
                    FOREIGN KEY (year_id) REFERENCES years (id)
                );

                CREATE TABLE IF NOT EXISTS subjects (
                    id TEXT PRIMARY KEY,
                    semester_id TEXT NOT NULL,
                    subject_code TEXT NOT NULL UNIQUE,
                    subject_name TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (semester_id) REFERENCES semesters (id)
                );

                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    subject_id TEXT NOT NULL,
                    experiment_number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    is_published INTEGER DEFAULT 1,
                    FOREIGN KEY (subject_id) REFERENCES subjects (id),
                    UNIQUE (subject_id, experiment_number)
                );

                CREATE TABLE IF NOT EXISTS experiment_versions (
                    id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    version_number INTEGER DEFAULT 1,
                    storage_path TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (id)
                );
                """
            )
            # Check if seed data is needed
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM years")
            if cur.fetchone()[0] == 0:
                self._seed_default_data(conn)

    def _seed_default_data(self, conn: sqlite3.Connection) -> None:
        """Insert default demonstration catalog and populate local cache."""
        for yr in SEED_YEARS:
            conn.execute(
                "INSERT INTO years (id, year_number, display_name) VALUES (?, ?, ?)",
                (yr["id"], yr["year_number"], yr["display_name"]),
            )

        for sem in SEED_SEMESTERS:
            conn.execute(
                "INSERT INTO semesters (id, year_id, semester_number, display_name) VALUES (?, ?, ?, ?)",
                (sem["id"], sem["year_id"], sem["semester_number"], sem["display_name"]),
            )

        for sub in SEED_SUBJECTS:
            conn.execute(
                "INSERT INTO subjects (id, semester_id, subject_code, subject_name) VALUES (?, ?, ?, ?)",
                (sub["id"], sub["semester_id"], sub["subject_code"], sub["subject_name"]),
            )

        config.cache_dir.mkdir(parents=True, exist_ok=True)
        for exp in SEED_EXPERIMENTS:
            conn.execute(
                """INSERT INTO experiments
                (id, subject_id, experiment_number, title, description)
                VALUES (?, ?, ?, ?, ?)""",
                (exp["id"], exp["subject_id"], exp["experiment_number"], exp["title"], exp["description"]),
            )

            filename = exp["filename"]
            sha = get_demo_hash(filename)
            conn.execute(
                """INSERT INTO experiment_versions
                (id, experiment_id, version_number, storage_path, filename, sha256)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (f"ver-{exp['id']}", exp["id"], 1, f"programs/{filename}", filename, sha),
            )

            # Pre-populate demo file in cache for seamless offline first run
            cached_file = config.cache_dir / filename
            if not cached_file.exists():
                cached_file.write_text(DEMO_PROGRAMS.get(filename, ""), encoding="utf-8")

        conn.commit()

    def get_years(self) -> list[Year]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT id, year_number, display_name FROM years ORDER BY year_number ASC").fetchall()
            return [Year(**dict(r)) for r in rows]

    def get_subjects_by_year(self, year_number: int) -> list[Subject]:
        with self._get_connection() as conn:
            query = """
                SELECT s.id, s.semester_id, s.subject_code, s.subject_name, s.is_active,
                       sem.display_name as semester_label
                FROM subjects s
                JOIN semesters sem ON s.semester_id = sem.id
                JOIN years y ON sem.year_id = y.id
                WHERE y.year_number = ? AND s.is_active = 1
                ORDER BY sem.semester_number ASC, s.subject_name ASC
            """
            rows = conn.execute(query, (year_number,)).fetchall()
            return [Subject(**dict(r)) for r in rows]

    def get_experiments_by_subject(self, subject_id: str) -> list[Experiment]:
        with self._get_connection() as conn:
            query = """
                SELECT e.id, e.subject_id, e.experiment_number, e.title, e.description, e.is_published,
                       v.id as v_id, v.version_number as v_version, v.storage_path as v_storage,
                       v.filename as v_filename, v.sha256 as v_sha
                FROM experiments e
                LEFT JOIN experiment_versions v ON e.id = v.experiment_id
                WHERE e.subject_id = ? AND e.is_published = 1
                ORDER BY e.experiment_number ASC
            """
            rows = conn.execute(query, (subject_id,)).fetchall()
            experiments = []
            for r in rows:
                v = None
                if r["v_id"]:
                    v = ExperimentVersion(
                        id=r["v_id"],
                        experiment_id=r["id"],
                        version_number=r["v_version"],
                        storage_path=r["v_storage"],
                        filename=r["v_filename"],
                        sha256=r["v_sha"],
                    )
                experiments.append(
                    Experiment(
                        id=r["id"],
                        subject_id=r["subject_id"],
                        experiment_number=r["experiment_number"],
                        title=r["title"],
                        description=r["description"] or "",
                        is_published=bool(r["is_published"]),
                        current_version=v,
                    )
                )
            return experiments

    def get_experiment_by_index(self, subject_id: str, index: int) -> Optional[Experiment]:
        experiments = self.get_experiments_by_subject(subject_id)
        for exp in experiments:
            if exp.experiment_number == index:
                return exp
        return None

    def get_latest_version(self, experiment_id: str) -> Optional[ExperimentVersion]:
        with self._get_connection() as conn:
            row = conn.execute(
                """SELECT id, experiment_id, version_number, storage_path, filename, sha256
                FROM experiment_versions
                WHERE experiment_id = ?
                ORDER BY version_number DESC LIMIT 1""",
                (experiment_id,),
            ).fetchone()
            if row:
                return ExperimentVersion(**dict(row))
            return None
