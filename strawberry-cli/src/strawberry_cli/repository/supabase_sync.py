"""Supabase catalog synchronization and remote file pre-caching."""

import json
import time
from datetime import datetime
from typing import Any, Optional
import httpx

from strawberry_cli.core.config import config
from strawberry_cli.repository.sqlite_repo import SQLiteCatalogRepository
from strawberry_cli.services.cache import cache_service


class SupabaseSyncService:
    """Synchronizes the local SQLite database and file cache with Supabase."""

    def __init__(self, repo: Optional[SQLiteCatalogRepository] = None):
        self.repo = repo or SQLiteCatalogRepository()
        self.supabase_url = config.supabase_url.rstrip("/")
        self.publishable_key = config.supabase_publishable_key

    def is_configured(self) -> bool:
        """Checks if remote Supabase credentials are configured."""
        return bool(self.supabase_url and self.publishable_key)

    def is_online(self) -> bool:
        """Fast connectivity check with bounded timeout."""
        if not self.is_configured():
            return False
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.head(self.supabase_url)
                return res.status_code < 500
        except Exception:
            return False

    def _get_headers(self) -> dict[str, str]:
        return {
            "apikey": self.publishable_key,
            "Authorization": f"Bearer {self.publishable_key}",
            "Content-Type": "application/json",
        }

    def sync(self) -> dict[str, Any]:
        """Performs a full synchronization cycle if online."""
        if not self.is_online():
            return {"status": "offline", "synced": False, "timestamp": time.time()}

        headers = self._get_headers()
        base_rest = f"{self.supabase_url}/rest/v1"

        try:
            with httpx.Client(timeout=config.network_timeout_seconds) as client:
                # 1. Fetch remote catalog tables
                years = client.get(f"{base_rest}/years?select=*", headers=headers).json()
                semesters = client.get(f"{base_rest}/semesters?select=*", headers=headers).json()
                subjects = client.get(f"{base_rest}/subjects?select=*&is_active=eq.true", headers=headers).json()
                experiments = client.get(
                    f"{base_rest}/experiments?select=*&is_published=eq.true", headers=headers
                ).json()
                versions = client.get(f"{base_rest}/experiment_versions?select=*", headers=headers).json()

                # 2. Reconcile with local SQLite database
                with self.repo._get_connection() as conn:
                    for y in years:
                        conn.execute(
                            "INSERT OR REPLACE INTO years (id, year_number, display_name) VALUES (?, ?, ?)",
                            (y["id"], y["year_number"], y["display_name"]),
                        )
                    for s in semesters:
                        conn.execute(
                            "INSERT OR REPLACE INTO semesters (id, year_id, semester_number, display_name) VALUES (?, ?, ?, ?)",
                            (s["id"], s["year_id"], s["semester_number"], s["display_name"]),
                        )
                    for sub in subjects:
                        conn.execute(
                            "INSERT OR REPLACE INTO subjects (id, semester_id, subject_code, subject_name, is_active) VALUES (?, ?, ?, ?, ?)",
                            (sub["id"], sub["semester_id"], sub["subject_code"], sub["subject_name"], int(sub.get("is_active", True))),
                        )
                    for exp in experiments:
                        conn.execute(
                            "INSERT OR REPLACE INTO experiments (id, subject_id, experiment_number, title, description, is_published) VALUES (?, ?, ?, ?, ?, ?)",
                            (exp["id"], exp["subject_id"], exp["experiment_number"], exp["title"], exp.get("description", ""), int(exp.get("is_published", True))),
                        )
                    for v in versions:
                        conn.execute(
                            "INSERT OR REPLACE INTO experiment_versions (id, experiment_id, version_number, storage_path, filename, sha256) VALUES (?, ?, ?, ?, ?, ?)",
                            (v["id"], v["experiment_id"], v.get("version_number", 1), v["storage_path"], v["filename"], v["sha256"]),
                        )
                    conn.commit()

                # 3. Pre-download any missing or updated source files
                files_downloaded = 0
                for v in versions:
                    filename = v["filename"]
                    expected_sha = v["sha256"]
                    storage_path = v["storage_path"].lstrip("/")

                    # Check if file already cached and valid
                    if not cache_service.verify_integrity(filename, expected_sha):
                        # Download from Supabase Storage public URL
                        storage_url = f"{self.supabase_url}/storage/v1/object/public/{storage_path}"
                        file_res = client.get(storage_url, headers=headers)
                        if file_res.status_code == 200:
                            cache_service.save_file(filename, file_res.content, expected_sha)
                            files_downloaded += 1

                # 4. Record sync state
                state = {
                    "status": "success",
                    "synced": True,
                    "last_sync": datetime.utcnow().isoformat(),
                    "files_downloaded": files_downloaded,
                }
                config.sync_state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
                return state

        except Exception as e:
            return {"status": "error", "error": str(e), "synced": False, "timestamp": time.time()}


supabase_sync = SupabaseSyncService()
