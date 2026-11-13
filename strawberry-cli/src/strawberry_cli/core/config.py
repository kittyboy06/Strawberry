"""Configuration and environment management for Strawberry."""

import os
import sys
from pathlib import Path
from pydantic import BaseModel, Field


class StrawberryConfig(BaseModel):
    """Runtime configuration for Strawberry CLI."""

    app_name: str = "Strawberry"
    version: str = "0.1.0"
    tagline: str = "Pick your program. Paste your code."

    # Timeout settings
    input_timeout_seconds: float = 7.0
    network_timeout_seconds: float = 10.0
    daemon_poll_interval_seconds: int = 240  # 4 minutes

    # Local storage paths
    local_app_data: Path = Field(
        default_factory=lambda: (
            Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            / "Strawberry"
            if sys.platform == "win32"
            else Path.home() / ".strawberry"
        )
    )

    # Supabase remote configuration (defaults to mock/demo if empty)
    supabase_url: str = os.getenv("STRAWBERRY_SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("STRAWBERRY_SUPABASE_ANON_KEY", "")

    @property
    def database_path(self) -> Path:
        return self.local_app_data / "catalog.db"

    @property
    def cache_dir(self) -> Path:
        return self.local_app_data / "cache"

    @property
    def sync_state_path(self) -> Path:
        return self.local_app_data / "sync_state.json"

    def ensure_directories(self) -> None:
        """Ensure all required local directories exist."""
        self.local_app_data.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


config = StrawberryConfig()
