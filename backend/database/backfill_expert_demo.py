"""Safely backfill the four seeded Class 8 misconception questions.

This script is additive and does not reset the database. It is safe to run on
an existing local project after the misconception migrations have been merged.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.database import fetch_one, initialize_database
from backend.database.seed import MISCONCEPTION_SEED, load_seed_data
from backend.services.question_authoring import create_question_with_tagged_options


def backfill() -> None:
    initialize_database()
    data = load_seed_data()
    questions = {int(row["id"]): row for row in data["questions"]}
    added = 0
    skipped = 0

    for question_id, steps in MISCONCEPTION_SEED.items():
        question = questions.get(question_id)
        if not question:
            raise RuntimeError(f"Seed question {question_id} was not found in seed_data.json")
        existing_steps = fetch_one(
            "SELECT id FROM question_steps WHERE question_id = ? LIMIT 1",
            (question_id,),
        )
        existing_options = fetch_one(
            "SELECT id FROM question_options WHERE question_id = ? LIMIT 1",
            (question_id,),
        )
        if existing_steps or existing_options:
            skipped += 1
            continue

        create_question_with_tagged_options(
            question_id=question_id,
            question_text=question["question_text"],
            correct_answer=question["correct_answer"],
            steps=steps,
            teacher_id=7,
            concept_id=2,
            difficulty=question["difficulty"],
        )
        added += 1

    print(f"Expert demo backfill complete. Added: {added}. Already present: {skipped}.")


if __name__ == "__main__":
    backfill()
