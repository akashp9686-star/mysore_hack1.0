from fastapi import APIRouter, HTTPException
from backend.database.database import fetch_all, fetch_one
from backend.services.adaptive_engine import evaluate_student

router = APIRouter(prefix="/facilitator", tags=["facilitator"])


@router.get("/students")
def students_needing_attention():
    rows = fetch_all(
        """
        SELECT sp.student_id, s.name,
               c.name AS weak_concept,
               sp.accuracy, sp.status
        FROM student_progress sp
        JOIN students s ON s.id = sp.student_id
        JOIN concepts c ON c.id = sp.concept_id
        WHERE sp.status = 'needs_intervention'
        ORDER BY sp.accuracy ASC, sp.student_id ASC
        """
    )
    return {"students": [dict(row) for row in rows]}


@router.get("/students/{student_id}")
def facilitator_student(student_id: int):
    student = fetch_one(
        """
        SELECT s.id, s.name, s.grade, sub.name AS subject, t.name AS topic
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
    if not student:
        raise HTTPException(404, detail={"error": "student_not_found", "message": "Student not found."})

    progress_rows = fetch_all(
        """
        SELECT sp.concept_id, c.name, sp.accuracy, sp.attempt_count, sp.status, sp.updated_at
        FROM student_progress sp
        JOIN concepts c ON c.id = sp.concept_id
        WHERE sp.student_id = ?
        ORDER BY sp.accuracy ASC, c.id ASC
        """,
        (student_id,),
    )

    weak = progress_rows[0] if progress_rows else None
    evidence = {}
    attempts = []
    if weak:
        evidence = evaluate_student(student_id, weak["concept_id"])
        attempts = fetch_all(
            """
            SELECT a.id, a.question_id, q.question_text, a.answer, a.is_correct, a.time_taken, a.created_at
            FROM attempts a
            JOIN questions q ON q.id = a.question_id
            WHERE a.student_id = ? AND q.concept_id = ?
            ORDER BY a.id DESC
            LIMIT 12
            """,
            (student_id, weak["concept_id"]),
        )

    interventions = fetch_all(
        """
        SELECT i.id, i.concept_id, c.name AS concept_name, i.type, i.teacher_id,
               i.status, i.result, i.created_at, t.name AS teacher_name
        FROM interventions i
        JOIN concepts c ON c.id = i.concept_id
        LEFT JOIN teachers t ON t.id = i.teacher_id
        WHERE i.student_id = ?
        ORDER BY i.id DESC
        """,
        (student_id,),
    )

    return {
        "student": dict(student),
        "concept_progress": [dict(r) for r in progress_rows],
        "weak_concept": dict(weak) if weak else None,
        "evidence": evidence,
        "attempts": [dict(r) for r in attempts],
        "interventions": [dict(r) for r in interventions],
    }
