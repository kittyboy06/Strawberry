"""Abstract Base Repository for academic catalog operations."""

from abc import ABC, abstractmethod
from typing import Optional
from strawberry_cli.models import Year, Subject, Experiment, ExperimentVersion


class BaseCatalogRepository(ABC):
    """Interface for retrieving and managing academic catalog data."""

    @abstractmethod
    def get_years(self) -> list[Year]:
        """Retrieve all active academic years."""
        pass

    @abstractmethod
    def get_subjects_by_year(self, year_number: int) -> list[Subject]:
        """Retrieve all subjects across both semesters for a given year."""
        pass

    @abstractmethod
    def get_experiments_by_subject(self, subject_id: str) -> list[Experiment]:
        """Retrieve all laboratory experiments for a given subject."""
        pass

    @abstractmethod
    def get_experiment_by_index(self, subject_id: str, index: int) -> Optional[Experiment]:
        """Retrieve a specific experiment by subject and its numeric index."""
        pass

    @abstractmethod
    def get_latest_version(self, experiment_id: str) -> Optional[ExperimentVersion]:
        """Retrieve the latest version metadata for an experiment."""
        pass
