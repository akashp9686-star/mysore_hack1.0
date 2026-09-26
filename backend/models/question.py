from dataclasses import dataclass
from typing import Optional

@dataclass
class Question:
    id: int
    concept_id: int
    question_text: str
    difficulty: str
    correct_answer: str
