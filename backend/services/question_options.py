"""Presentation-layer answer choices for seeded MCQs."""

import json
from pathlib import Path

OPTIONS = {
    1: ["x = 7", "x = 17", "x = 5", "x = -7"],
    2: ["x = 6", "x = 15", "x = 21", "x = 3"],
    3: ["x = 5", "x = 13", "x = 9", "x = 17"],
    4: ["x = 5", "x = 15", "x = 3", "x = -5"],
    5: ["x = 5", "x = 10", "x = 12", "x = 2"],
    6: ["x = 7", "x = 14", "x = 1", "x = 9"],
    7: ["x = 13", "x = 5", "x = -13", "x = 9"],
    8: ["x = 5", "x = 11", "x = 4", "x = 10"],
    9: ["5x", "6x", "5x + 2", "x²"],
    10: ["3a + 3", "5a + 3", "3a + 4", "4a + 3"],
}

_CLASS_OPTIONS = Path(__file__).resolve().parents[2] / "data" / "class_question_options.json"
if _CLASS_OPTIONS.exists():
    OPTIONS.update({int(k): v for k, v in json.loads(_CLASS_OPTIONS.read_text(encoding="utf-8")).items()})


def get_options(question_id: int) -> list[str]:
    return OPTIONS.get(question_id, [])
