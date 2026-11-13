"""Laboratory Experiment and Version models."""

from typing import Optional
from pydantic import BaseModel


class ExperimentVersion(BaseModel):
    """Specific version of an experiment's source code file."""

    id: str
    experiment_id: str
    version_number: int = 1
    storage_path: str  # Remote Supabase Storage path
    filename: str  # e.g. "SocketServer.java"
    sha256: str
    created_at: Optional[str] = None


class Experiment(BaseModel):
    """A laboratory experiment within a subject."""

    id: str
    subject_id: str
    experiment_number: int  # 1, 2, 3...
    title: str  # "Socket Programming"
    description: str = ""
    is_published: bool = True
    current_version: Optional[ExperimentVersion] = None

    @property
    def formatted_index(self) -> str:
        """Formatted two-digit index (e.g. '01', '02')."""
        return f"{self.experiment_number:02d}"
