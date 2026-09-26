"""Rule-based struggle detection for the HackMysore MVP."""

from backend.database.database import fetch_one

NORMAL_THRESHOLD = 80
PRACTICE_THRESHOLD = 50
MIN_ATTEMPTS = 3
RECENT_WINDOW = 3


def get_concept_evidence(student_id: int, concept_id: int) -> dict:
    row = fetch_one(
        """
        SELECT COUNT(*) AS attempts,
               COALESCE(SUM(is_correct), 0) AS correct
        FROM attempts
        WHERE student_id = ?
          AND question_id IN (SELECT id FROM questions WHERE concept_id = ?)
        """,
        (student_id, concept_id),
    )
    attempts = int(row["attempts"])
    correct = int(row["correct"])
    accuracy = round((correct / attempts) * 100, 2) if attempts else 0.0

    recent = fetch_one(
        """
        SELECT COUNT(*) AS attempts,
               COALESCE(SUM(is_correct), 0) AS correct
        FROM (
            SELECT is_correct
            FROM attempts
            WHERE student_id = ?
              AND question_id IN (SELECT id FROM questions WHERE concept_id = ?)
            ORDER BY id DESC
            LIMIT ?
        )
        """,
        (student_id, concept_id, RECENT_WINDOW),
    )
    recent_attempts = int(recent["attempts"])
    recent_correct = int(recent["correct"])
    recent_accuracy = round((recent_correct / recent_attempts) * 100, 2) if recent_attempts else 0.0

    return {
        "attempts": attempts,
        "accuracy": accuracy,
        "recent_attempts": recent_attempts,
        "recent_accuracy": recent_accuracy,
    }


def detect_status(student_id: int, concept_id: int) -> dict:
    evidence = get_concept_evidence(student_id, concept_id)
    attempts = evidence["attempts"]
    accuracy = evidence["accuracy"]
    recent_accuracy = evidence["recent_accuracy"]

    # One or two mistakes are not enough evidence of a learning difficulty.
    if attempts < MIN_ATTEMPTS:
        return {
            **evidence,
            "status": "normal",
            "reason": "Insufficient evidence for struggle detection.",
        }

    if evidence["recent_attempts"] >= MIN_ATTEMPTS and recent_accuracy < PRACTICE_THRESHOLD:
        return {
            **evidence,
            "status": "needs_intervention",
            "reason": "Repeated incorrect answers on the concept.",
        }

    if accuracy < PRACTICE_THRESHOLD:
        return {
            **evidence,
            "status": "needs_intervention",
            "reason": "Low accuracy on the concept.",
        }

    if accuracy < NORMAL_THRESHOLD:
        return {
            **evidence,
            "status": "practice",
            "reason": "Additional practice is recommended.",
        }

    return {
        **evidence,
        "status": "normal",
        "reason": "Performance is currently on track.",
    }
