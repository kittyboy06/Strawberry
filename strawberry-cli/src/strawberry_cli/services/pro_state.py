"""Persistent local bookmarks and copy history for Strawberry Pro."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from strawberry_cli.core.config import config


class ProStateService:
    """Manages bookmarks and recent program history in %LOCALAPPDATA%\\Strawberry\\pro_state.json."""

    def __init__(self, state_path: Optional[Path] = None, max_history: int = 15):
        self.state_path = state_path or config.pro_state_path
        self.max_history = max_history

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"bookmarks": [], "history": []}
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return {"bookmarks": [], "history": []}
            bookmarks = raw.get("bookmarks", [])
            history = raw.get("history", [])
            return {
                "bookmarks": bookmarks if isinstance(bookmarks, list) else [],
                "history": history if isinstance(history, list) else [],
            }
        except Exception:
            return {"bookmarks": [], "history": []}

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.state_path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tmp_path.replace(self.state_path)

    def get_bookmarks(self) -> list[str]:
        """Returns bookmarked experiment IDs."""
        return list(self._load_state()["bookmarks"])

    def is_bookmarked(self, experiment_id: str) -> bool:
        """Checks whether an experiment ID is bookmarked."""
        return experiment_id in self._load_state()["bookmarks"]

    def toggle_bookmark(self, experiment_id: str) -> bool:
        """Toggles bookmark state for an experiment and returns its new state."""
        state = self._load_state()
        bookmarks: list[str] = state["bookmarks"]
        if experiment_id in bookmarks:
            bookmarks.remove(experiment_id)
            now_bookmarked = False
        else:
            bookmarks.append(experiment_id)
            now_bookmarked = True
        state["bookmarks"] = bookmarks
        self._save_state(state)
        return now_bookmarked

    def get_history(self) -> list[dict[str, Any]]:
        """Returns recent copied experiments (most recent first)."""
        return list(self._load_state()["history"])

    def record_history(
        self,
        experiment_id: str,
        title: str,
        subject_code: str,
        filename: str,
    ) -> None:
        """Records a verified program copy in history, keeping latest entries at the top."""
        state = self._load_state()
        history: list[dict[str, Any]] = [
            entry for entry in state["history"] if entry.get("experiment_id") != experiment_id
        ]
        history.insert(
            0,
            {
                "experiment_id": experiment_id,
                "title": title,
                "subject_code": subject_code,
                "filename": filename,
                "copied_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        state["history"] = history[: self.max_history]
        self._save_state(state)


pro_state_service = ProStateService()
