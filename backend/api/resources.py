from fastapi import APIRouter, HTTPException

from backend.database.database import fetch_one
from backend.services.resource_service import resources_for_concept

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/{concept_id}")
def resources(concept_id: int):
    if not fetch_one("SELECT id FROM concepts WHERE id = ?", (concept_id,)):
        raise HTTPException(404, detail={"error": "concept_not_found", "message": "Concept not found."})
    return {"concept_id": concept_id, "resources": [dict(x) for x in resources_for_concept(concept_id)]}
