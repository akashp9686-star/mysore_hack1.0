from fastapi import APIRouter, HTTPException

from backend.database.database import fetch_one, fetch_all
from backend.services.adaptive_engine import evaluate_student

router = APIRouter(prefix="/students", tags=["students"])


def student_not_found(student_id: int):
    raise HTTPException(
        status_code=404,
        detail={
            "error": "student_not_found",
            "message": f"Student with ID {student_id} was not found.",
        },
    )


@router.get("/{student_id}")
def get_student(student_id: int):
    row = fetch_one(
        """
        SELECT s.id, s.name, s.grade,
               sub.name AS current_subject,
               t.name AS current_topic
        FROM students s
        LEFT JOIN assessments a ON a.student_id = s.id
        LEFT JOIN topics t ON t.id = a.topic_id
        LEFT JOIN subjects sub ON sub.id = t.subject_id
        WHERE s.id = ?
        ORDER BY a.id DESC
        LIMIT 1
        """,
        (student_id,),
    )
    if not row:
        student_not_found(student_id)
    return dict(row)


@router.get("/{student_id}/intervention")
def get_student_intervention(student_id: int):
    if not fetch_one("SELECT id FROM students WHERE id = ?", (student_id,)):
        student_not_found(student_id)

    row = fetch_one(
        """
        SELECT sp.concept_id, c.name AS concept_name,
               t.id AS topic_id, t.name AS topic_name,
               sub.name AS subject_name
        FROM student_progress sp
        JOIN concepts c ON c.id = sp.concept_id
        JOIN topics t ON t.id = c.topic_id
        JOIN subjects sub ON sub.id = t.subject_id
        WHERE sp.student_id = ? AND sp.status = 'needs_intervention'
        ORDER BY sp.accuracy ASC, sp.updated_at DESC
        LIMIT 1
        """,
        (student_id,),
    )

    if not row:
        return {
            "student_id": student_id,
            "type": "none",
            "reason": "No concept currently requires intervention.",
            "teacher_required": False,
        }

    result = evaluate_student(student_id, row["concept_id"])
    return {
        "student_id": student_id,
        "concept_id": row["concept_id"],
        "concept_name": row["concept_name"],
        "topic_id": row["topic_id"],
        "topic_name": row["topic_name"],
        "subject_name": row["subject_name"],
        "type": result["recommended_action"],
        "reason": result["reason"],
        "teacher_required": result["teacher_required"],
    }
