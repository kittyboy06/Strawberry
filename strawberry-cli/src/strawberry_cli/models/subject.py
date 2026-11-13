"""Subject model representing courses with laboratory components."""

from pydantic import BaseModel


class Subject(BaseModel):
    """A laboratory subject belonging to a specific semester."""

    id: str
    semester_id: str
    subject_code: str  # e.g. "CS301"
    subject_name: str  # e.g. "Computer Networks"
    is_active: bool = True
    semester_label: str = ""  # e.g. "Semester 3" (populated for display)
