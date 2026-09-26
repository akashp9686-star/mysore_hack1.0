from dataclasses import dataclass
from typing import Optional

@dataclass
class Assessment:
    id: int
    student_id: int
    topic_id: int
    assessment_type: str
    created_at: str
