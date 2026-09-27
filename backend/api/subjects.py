from fastapi import APIRouter

from backend.database.database import fetch_all

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("")
def list_subjects():
    rows = fetch_all("SELECT id, name FROM subjects ORDER BY id")
    return {"subjects": [dict(row) for row in rows]}
