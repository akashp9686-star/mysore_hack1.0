from dataclasses import dataclass
from typing import Optional

@dataclass
class Concept:
    id: int
    topic_id: int
    name: str
