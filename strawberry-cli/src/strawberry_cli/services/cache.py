"""Local program file cache management and SHA-256 verification."""

import hashlib
from pathlib import Path
from typing import Optional
from strawberry_cli.core.config import config


class CacheService:
    """Manages the %LOCALAPPDATA%\\Strawberry\\cache directory."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or config.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_file_path(self, filename: str) -> Path:
        """Returns the absolute path to a cached file."""
        return self.cache_dir / filename

    def is_cached(self, filename: str) -> bool:
        """Checks if a file exists in the cache."""
        return self.get_file_path(filename).is_file()

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        """Calculates the SHA-256 hash of a local file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest().lower()

    def verify_integrity(self, filename: str, expected_sha256: str) -> bool:
        """Validates that the cached file matches the expected SHA-256 checksum."""
        file_path = self.get_file_path(filename)
        if not file_path.exists():
            return False
        actual_sha = self.calculate_sha256(file_path)
        return actual_sha.lower() == expected_sha256.lower()

    def read_source_code(self, filename: str) -> str:
        """Reads the source code content with UTF-8 encoding."""
        file_path = self.get_file_path(filename)
        return file_path.read_text(encoding="utf-8", errors="replace")

    def save_file(self, filename: str, content: bytes, expected_sha256: str) -> Path:
        """Atomically saves and verifies a downloaded file in cache."""
        temp_path = self.cache_dir / f"{filename}.tmp"
        temp_path.write_bytes(content)

        actual_sha = self.calculate_sha256(temp_path)
        if actual_sha.lower() != expected_sha256.lower():
            temp_path.unlink(missing_ok=True)
            raise ValueError(
                f"SHA-256 integrity verification failed for {filename}! "
                f"Expected: {expected_sha256}, Got: {actual_sha}"
            )

        target_path = self.get_file_path(filename)
        temp_path.replace(target_path)
        return target_path


cache_service = CacheService()
