
import sqlite3

from backend.database.database import DB_PATH, get_db, initialize_database
from backend.database.seed import seed_database


EXPECTED_TABLES = {
    "students", "teachers", "subjects", "topics", "concepts", "questions",
    "assessments", "attempts", "student_progress", "interventions",
    "learning_resources", "recommendations",
}


def test_seed_creates_expected_tables():
    seed_database()
    with get_db() as db:
        tables = {
            row["name"]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert EXPECTED_TABLES.issubset(tables)


def test_foreign_keys_enabled():
    initialize_database()
    with get_db() as db:
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_seed_has_three_demo_students():
    seed_database()
    with get_db() as db:
        count = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    assert count == 3


def test_progress_is_unique_per_student_and_concept():
    seed_database()
    with get_db() as db:
        with __import__("pytest").raises(sqlite3.IntegrityError):
            db.execute(
                """INSERT INTO student_progress
                   (student_id, concept_id, accuracy, attempt_count, status)
                   VALUES (102, 2, 20, 5, 'needs_intervention')"""
            )


def test_invalid_topic_foreign_key_is_rejected():
    initialize_database()
    with get_db() as db:
        with __import__("pytest").raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO topics (id, subject_id, name) VALUES (999, 999, 'Bad Topic')"
            )


def test_attempt_student_must_match_assessment_student():
    seed_database()
    with get_db() as db:
        with __import__("pytest").raises(sqlite3.IntegrityError):
            db.execute(
                """INSERT INTO attempts
                   (assessment_id, student_id, question_id, answer, is_correct, time_taken)
                   VALUES (1, 102, 3, 'x = 5', 1, 20)"""
            )
