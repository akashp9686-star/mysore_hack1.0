from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database.database import fetch_one, execute
from backend.services.adaptive_engine import evaluate_student

router = APIRouter(prefix="/interventions", tags=["interventions"])


class InterventionRequest(BaseModel):
    student_id: int = Field(gt=0)
    concept_id: int = Field(gt=0)
    type: str
    teacher_id: int | None = Field(default=None, gt=0)


@router.post("")
def create_intervention(payload: InterventionRequest):
    if not fetch_one("SELECT id FROM students WHERE id = ?", (payload.student_id,)):
        raise HTTPException(404, detail={"error": "student_not_found", "message": "Student not found."})
    if not fetch_one("SELECT id FROM concepts WHERE id = ?", (payload.concept_id,)):
        raise HTTPException(404, detail={"error": "concept_not_found", "message": "Concept not found."})
    if payload.teacher_id is not None and not fetch_one("SELECT id FROM teachers WHERE id = ?", (payload.teacher_id,)):
        raise HTTPException(404, detail={"error": "teacher_not_found", "message": "Teacher not found."})

    allowed = {"targeted_practice", "learning_resource", "teacher_session", "reassessment"}
    if payload.type not in allowed:
        raise HTTPException(400, detail={"error": "invalid_intervention_type", "message": "Unsupported intervention type."})
    if payload.type == "teacher_session" and payload.teacher_id is None:
        raise HTTPException(400, detail={"error": "teacher_required", "message": "teacher_id is required for a teacher session."})

    intervention_id = execute(
        """
        INSERT INTO interventions(student_id, concept_id, type, teacher_id, status)
        VALUES (?, ?, ?, ?, 'in_progress')
        """,
        (payload.student_id, payload.concept_id, payload.type, payload.teacher_id),
    )
    return {"intervention_id": intervention_id, "status": "in_progress"}


@router.get("/student/{student_id}")
def legacy_student_intervention(student_id: int):
    """Backward-compatible route; the contract route is on /students/{id}/intervention."""
    return _get_intervention(student_id)


def _get_intervention(student_id: int):
    if not fetch_one("SELECT id FROM students WHERE id = ?", (student_id,)):
        raise HTTPException(404, detail={"error": "student_not_found", "message": "Student not found."})

    row = fetch_one(
        """
        SELECT sp.concept_id, c.name AS concept_name
        FROM student_progress sp
        JOIN concepts c ON c.id = sp.concept_id
        WHERE sp.student_id = ? AND sp.status = 'needs_intervention'
        ORDER BY sp.accuracy ASC
        LIMIT 1
        """,
        (student_id,),
    )
    if not row:
        return {"student_id": student_id, "type": "none", "teacher_required": False}

    result = evaluate_student(student_id, row["concept_id"])
    latest = fetch_one(
        "SELECT id, type, status FROM interventions WHERE student_id = ? AND concept_id = ? ORDER BY id DESC LIMIT 1",
        (student_id, row["concept_id"]),
    )
    return {
        "student_id": student_id,
        "intervention_id": latest["id"] if latest else None,
        "intervention_status": latest["status"] if latest else None,
        "concept_id": row["concept_id"],
        "concept_name": row["concept_name"],
        "type": result["recommended_action"],
        "reason": result["reason"],
        "teacher_required": result["teacher_required"],
    }


@router.post("/{intervention_id}/complete")
def complete_intervention(intervention_id: int, status: str, result: str = ""):
    if status not in {"successful", "unsuccessful"}:
        raise HTTPException(400, detail={"error": "invalid_status", "message": "Status must be successful or unsuccessful."})
    row = fetch_one("SELECT id FROM interventions WHERE id = ?", (intervention_id,))
    if not row:
        raise HTTPException(404, detail={"error": "intervention_not_found", "message": "Intervention not found."})
    execute("UPDATE interventions SET status = ?, result = ? WHERE id = ?", (status, result, intervention_id))
    return {"intervention_id": intervention_id, "status": status, "result": result}
