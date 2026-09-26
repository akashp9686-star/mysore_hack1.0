from dataclasses import dataclass
from typing import Optional

@dataclass
class Teacher:
    id: int
    name: str
    experience: int
    verification_status: str
    created_at: str
