from dataclasses import dataclass
from typing import Optional

@dataclass
class Attempt:
    id: int
    assessment_id: int
    student_id: int
    question_id: int
    answer: str
    is_correct: int
    time_taken: int
    created_at: str
