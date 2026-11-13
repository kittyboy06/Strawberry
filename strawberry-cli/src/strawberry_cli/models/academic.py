"""Academic hierarchy models: Years and Semesters."""

from typing import Optional
from pydantic import BaseModel, Field


class Year(BaseModel):
    """Represents an academic year (e.g., 2nd Year, 3rd Year, 4th Year)."""

    id: str
    year_number: int  # 2, 3, or 4
    display_name: str  # "2nd Year", "3rd Year", "4th Year"


class Semester(BaseModel):
    """Represents an academic semester belonging to a year."""

    id: str
    year_id: str
    semester_number: int  # 3 through 8
    display_name: str  # "Semester 3", "Semester 4", etc.
