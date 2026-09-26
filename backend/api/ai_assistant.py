from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database.database import fetch_one, fetch_all
from backend.ai.ai_service import answer_learning_question

router = APIRouter(prefix="/ai", tags=["ai-assistant"])


class AssistantRequest(BaseModel):
    student_id: int = Field(gt=0)
    message: str = Field(min_length=1, max_length=600)
    display_name: str | None = Field(default=None, max_length=100)


@router.post("/assistant")
def learning_assistant(payload: AssistantRequest):
    student = fetch_one(
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
        (payload.student_id,),
    )
    if not student:
        raise HTTPException(404, detail={"error": "student_not_found", "message": "Student not found."})

    progress = fetch_one(
        """
        SELECT COALESCE(AVG(accuracy), 0) AS overall_progress
        FROM student_progress
        WHERE student_id = ?
        """,
        (payload.student_id,),
    )
    concepts = fetch_all(
        """
        SELECT sp.concept_id, c.name, sp.accuracy, sp.attempt_count, sp.status
        FROM student_progress sp
        JOIN concepts c ON c.id = sp.concept_id
        WHERE sp.student_id = ?
        ORDER BY sp.accuracy ASC, sp.updated_at DESC
        """,
        (payload.student_id,),
    )
    latest_ai = fetch_one(
        """
        SELECT a.answer, a.is_correct, q.question_text, q.correct_answer, c.name AS concept_name
        FROM attempts a
        JOIN questions q ON q.id = a.question_id
        JOIN concepts c ON c.id = q.concept_id
        WHERE a.student_id = ?
        ORDER BY a.id DESC
        LIMIT 1
        """,
        (payload.student_id,),
    )
    intervention = fetch_one(
        """
        SELECT i.type, i.status, i.result, c.name AS concept_name
        FROM interventions i
        LEFT JOIN concepts c ON c.id = i.concept_id
        WHERE i.student_id = ?
        ORDER BY i.id DESC
        LIMIT 1
        """,
        (payload.student_id,),
    )

    weak = concepts[0] if concepts else None
    student_evidence = dict(student)
    if payload.display_name and payload.display_name.strip():
        student_evidence["name"] = payload.display_name.strip()
    evidence = {
        "student": student_evidence,
        "overall_progress": round(float(progress["overall_progress"] or 0), 1) if progress else 0,
        "concept_progress": [dict(x) for x in concepts],
        "weak_concept": dict(weak) if weak else None,
        "latest_attempt": dict(latest_ai) if latest_ai else None,
        "latest_intervention": dict(intervention) if intervention else None,
    }

    answer = answer_learning_question(payload.message, evidence)
    return {"answer": answer["answer"], "source": answer["source"], "evidence": evidence}
