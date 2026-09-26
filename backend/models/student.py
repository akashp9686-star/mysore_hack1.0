from dataclasses import dataclass
from typing import Optional

@dataclass
class Student:
    id: int
    name: str
    grade: int
    created_at: str
