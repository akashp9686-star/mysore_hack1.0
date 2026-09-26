"""Adaptive-learning decision engine.

The engine is deliberately rule-based for the MVP. AI can provide advisory
information later, but core learning decisions remain deterministic.
"""

from backend.database.database import fetch_one
from backend.services.struggle_detector import detect_status


def evaluate_student(student_id: int, concept_id: int) -> dict:
    result = detect_status(student_id, concept_id)
    intervention = fetch_one(
        """
        SELECT type, status, result
        FROM interventions
        WHERE student_id = ? AND concept_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (student_id, concept_id),
    )

    if result["status"] == "needs_intervention":
        if intervention and (intervention["type"] == "teacher_session" or intervention["status"] == "unsuccessful"):
            return {
                **result,
                "recommended_action": "teacher_session",
                "teacher_required": True,
            }
        return {
            **result,
            "recommended_action": "targeted_practice",
            "teacher_required": False,
        }

    if result["status"] == "practice":
        return {
            **result,
            "recommended_action": "additional_practice",
            "teacher_required": False,
        }

    # A successful recent intervention means the student can continue.
    if intervention and intervention["status"] == "successful":
        return {
            **result,
            "recommended_action": "continue",
            "teacher_required": False,
        }

    return {
        **result,
        "recommended_action": "continue",
        "teacher_required": False,
    }


def database_status(adaptive_status: str) -> str:
    """Map engine states to the shared DB status enum."""
    if adaptive_status == "needs_intervention":
        return "needs_intervention"
    return "normal"
