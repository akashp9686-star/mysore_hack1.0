from dataclasses import dataclass
from typing import Optional

@dataclass
class StudentProgress:
    id: int
    student_id: int
    concept_id: int
    accuracy: float
    attempt_count: int
    status: str
    updated_at: str
