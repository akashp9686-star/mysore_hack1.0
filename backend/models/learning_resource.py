from dataclasses import dataclass
from typing import Optional

@dataclass
class LearningResource:
    id: int
    concept_id: int
    title: str
    source: str
    url: str
    description: str | None
    resource_type: str
