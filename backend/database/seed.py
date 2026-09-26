
"""Create/reset the HackMysore demo database and load deterministic seed data."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from backend.database.database import DB_PATH, get_db, initialize_database, reset_database

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = PROJECT_ROOT / "data" / "seed_data.json"


def load_seed_data() -> dict:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def seed_database() -> None:
    reset_database()
    initialize_database()
    data = load_seed_data()

    with get_db() as conn:
        for row in data["students"]:
            conn.execute(
                "INSERT INTO students (id, name, grade) VALUES (?, ?, ?)",
                (row["id"], row["name"], row["grade"]),
            )

        for row in data["teachers"]:
            conn.execute(
                """INSERT INTO teachers
                   (id, name, experience, verification_status)
                   VALUES (?, ?, ?, ?)""",
                (row["id"], row["name"], row["experience"], row["verification_status"]),
            )

        for row in data["subjects"]:
            conn.execute(
                "INSERT INTO subjects (id, name) VALUES (?, ?)",
                (row["id"], row["name"]),
            )

        for row in data["topics"]:
            conn.execute(
                "INSERT INTO topics (id, subject_id, name) VALUES (?, ?, ?)",
                (row["id"], row["subject_id"], row["name"]),
            )

        for row in data["concepts"]:
            conn.execute(
                "INSERT INTO concepts (id, topic_id, name) VALUES (?, ?, ?)",
                (row["id"], row["topic_id"], row["name"]),
            )

        for row in data["questions"]:
            conn.execute(
                """INSERT INTO questions
                   (id, concept_id, question_text, difficulty, correct_answer)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    row["id"],
                    row["concept_id"],
                    row["question_text"],
                    row["difficulty"],
                    row["correct_answer"],
                ),
            )

        for row in data["assessments"]:
            conn.execute(
                """INSERT INTO assessments
                   (id, student_id, topic_id, assessment_type, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    row["id"],
                    row["student_id"],
                    row["topic_id"],
                    row["assessment_type"],
                    row["created_at"],
                ),
            )

        for row in data["attempts"]:
            conn.execute(
                """INSERT INTO attempts
                   (id, assessment_id, student_id, question_id, answer,
                    is_correct, time_taken, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["id"],
                    row["assessment_id"],
                    row["student_id"],
                    row["question_id"],
                    row["answer"],
                    row["is_correct"],
                    row["time_taken"],
                    row["created_at"],
                ),
            )

        for row in data["student_progress"]:
            conn.execute(
                """INSERT INTO student_progress
                   (id, student_id, concept_id, accuracy, attempt_count, status, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["id"],
                    row["student_id"],
                    row["concept_id"],
                    row["accuracy"],
                    row["attempt_count"],
                    row["status"],
                    row["updated_at"],
                ),
            )

        for row in data["interventions"]:
            conn.execute(
                """INSERT INTO interventions
                   (id, student_id, concept_id, type, teacher_id, status, result, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["id"],
                    row["student_id"],
                    row["concept_id"],
                    row["type"],
                    row["teacher_id"],
                    row["status"],
                    row["result"],
                    row["created_at"],
                ),
            )

        for row in data["learning_resources"]:
            conn.execute(
                """INSERT INTO learning_resources
                   (id, concept_id, title, source, url, description, resource_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["id"],
                    row["concept_id"],
                    row["title"],
                    row["source"],
                    row["url"],
                    row["description"],
                    row["resource_type"],
                ),
            )

        for row in data["recommendations"]:
            conn.execute(
                """INSERT INTO recommendations
                   (id, student_id, concept_id, resource_id, reason, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["id"],
                    row["student_id"],
                    row["concept_id"],
                    row["resource_id"],
                    row["reason"],
                    row["status"],
                    row["created_at"],
                ),
            )

    print(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    seed_database()
