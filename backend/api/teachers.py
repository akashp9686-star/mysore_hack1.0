from fastapi import APIRouter, HTTPException

from backend.database.database import fetch_one
from backend.services.teacher_matcher import match_teachers

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.get("/match")
def match(concept_id: int):
    if not fetch_one("SELECT id FROM concepts WHERE id = ?", (concept_id,)):
        raise HTTPException(404, detail={"error": "concept_not_found", "message": "Concept not found."})

    teachers = [dict(row) for row in match_teachers(concept_id)]
    return {
        "concept_id": concept_id,
        "teachers": teachers,
        "matching_note": (
            "Teacher subject/expertise are not stored in the current agreed schema. "
            "Candidates are therefore ordered by verification status and experience."
        ),
    }
