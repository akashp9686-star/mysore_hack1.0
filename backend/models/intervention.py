from dataclasses import dataclass
from typing import Optional

@dataclass
class Intervention:
    id: int
    student_id: int
    concept_id: int
    type: str
    teacher_id: int | None
    status: str
    result: str | None
    created_at: str
