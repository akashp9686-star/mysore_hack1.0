from dataclasses import dataclass
from typing import Optional

@dataclass
class Recommendation:
    id: int
    student_id: int
    concept_id: int
    resource_id: int
    reason: str
    status: str
    created_at: str
