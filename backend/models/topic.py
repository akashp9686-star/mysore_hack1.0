from dataclasses import dataclass
from typing import Optional

@dataclass
class Topic:
    id: int
    subject_id: int
    name: str
