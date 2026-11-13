"""Configuration and environment management for Strawberry."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field


def _load_environment() -> None:
    """Discovers and loads .env files from project root, working dir, or LocalAppData."""
    app_data = (
        Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        / "Strawberry"
        if sys.platform == "win32"
        else Path.home() / ".strawberry"
    )

    # Search candidates in priority order
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[4] / ".env",  # Workspace root
        Path(__file__).resolve().parents[3] / ".env",  # strawberry-cli root
        app_data / ".env",
    ]

    for candidate in candidates:
        if candidate.is_file():
            load_dotenv(candidate, override=False)


# Initialize environment on module import
_load_environment()


class StrawberryConfig(BaseModel):
    """Runtime configuration for Strawberry CLI."""

    app_name: str = "Strawberry"
    version: str = "0.1.0"
    tagline: str = "Pick your program. Paste your code."

    # Timeout settings
    input_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("STRAWBERRY_INPUT_TIMEOUT_SECONDS", "7.0"))
    )
    network_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("STRAWBERRY_NETWORK_TIMEOUT_SECONDS", "10.0"))
    )
    daemon_poll_interval_seconds: int = Field(
        default_factory=lambda: int(os.getenv("STRAWBERRY_DAEMON_POLL_INTERVAL_SECONDS", "240"))
    )

    # Local storage paths
    local_app_data: Path = Field(
        default_factory=lambda: (
            Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            / "Strawberry"
            if sys.platform == "win32"
            else Path.home() / ".strawberry"
        )
    )

    # Supabase remote configuration (Modern publishable & secret keys, with legacy anon fallback)
    supabase_url: str = Field(
        default_factory=lambda: (
            os.getenv("STRAWBERRY_SUPABASE_URL")
            or os.getenv("VITE_SUPABASE_URL")
            or ""
        )
    )
    supabase_publishable_key: str = Field(
        default_factory=lambda: (
            os.getenv("STRAWBERRY_SUPABASE_PUBLISHABLE_KEY")
            or os.getenv("VITE_SUPABASE_PUBLISHABLE_KEY")
            or os.getenv("STRAWBERRY_SUPABASE_ANON_KEY")
            or os.getenv("VITE_SUPABASE_ANON_KEY")
            or ""
        )
    )
    supabase_secret_key: str = Field(
        default_factory=lambda: (
            os.getenv("STRAWBERRY_SUPABASE_SECRET_KEY")
            or ""
        )
    )

    @property
    def base_supabase_url(self) -> str:
        """Normalized base Supabase URL stripped of trailing slashes and /rest/v1 paths."""
        url = self.supabase_url.strip().rstrip("/")
        if url.endswith("/rest/v1"):
            url = url[:-len("/rest/v1")].rstrip("/")
        return url

    @property
    def supabase_anon_key(self) -> str:
        """Alias for publishable key to maintain backward compatibility."""
        return self.supabase_publishable_key

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
