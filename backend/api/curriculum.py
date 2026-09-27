from fastapi import APIRouter, HTTPException

from backend.database.database import fetch_all, fetch_one
from backend.services.adaptive_engine import evaluate_student

router = APIRouter(prefix="/curriculum", tags=["curriculum"])

# Only Class 8 has live diagnostic content in this demo. The other class cards
# remain visible so the platform can show the intended K-9 shell, but they are
# explicitly marked as placeholders and do not create real assessments.
MATH_CLASSES = {
    5: {
        "title": "Class 5 Mathematics",
        "active": False,
        "status": "coming_soon",
        "topic_id": None,
        "concept_id": None,
        "topics": [],
        "videos": [],
    },
    6: {
        "title": "Class 6 Mathematics",
        "active": False,
        "status": "coming_soon",
        "topic_id": None,
        "concept_id": None,
        "topics": [],
        "videos": [],
    },
    7: {
        "title": "Class 7 Mathematics",
        "active": False,
        "status": "coming_soon",
        "topic_id": None,
        "concept_id": None,
        "topics": [],
        "videos": [],
    },
    8: {
        "title": "Class 8 Mathematics",
        "active": True,
        "status": "live_demo",
        # The expert feature is intentionally attached to the legacy demo path:
        # Topic 2 -> Linear Equations -> Variables on Both Sides (Concept 2).
        "topic_id": 2,
        "concept_id": 2,
        "topics": ["Algebra", "Linear Equations", "Variables on Both Sides"],
        "videos": [
            {"title": "Linear equations basics", "query": "Class 8 maths algebra linear equations variables on both sides"},
            {"title": "Variables on both sides", "query": "Class 8 maths variables on both sides linear equations"},
        ],
    },
    9: {
        "title": "Class 9 Mathematics",
        "active": False,
        "status": "coming_soon",
        "topic_id": None,
        "concept_id": None,
        "topics": [],
        "videos": [],
    },
}


@router.get("/math/classes")
def math_classes():
    return {"classes": [{"grade": grade, **data} for grade, data in MATH_CLASSES.items()]}


@router.get("/math/{grade}/progress/{student_id}")
def class_progress(grade: int, student_id: int):
    if grade not in MATH_CLASSES:
        raise HTTPException(404, detail={"error": "class_not_found", "message": "Only Classes 5–9 are available."})
    if not fetch_one("SELECT id FROM students WHERE id = ?", (student_id,)):
        raise HTTPException(404, detail={"error": "student_not_found", "message": "Student not found."})

    class_info = MATH_CLASSES[grade]
    if not class_info["active"]:
        return {
            "grade": grade,
            "active": False,
            "status": "coming_soon",
            "topic_id": None,
            "overall_progress": 0,
            "concept_progress": [],
        }

    concept_id = class_info["concept_id"]
    concept = fetch_one("SELECT id, name FROM concepts WHERE id = ?", (concept_id,))
    if not concept:
        return {"grade": grade, "active": True, "topic_id": class_info["topic_id"], "overall_progress": 0, "concept_progress": []}

    evidence = evaluate_student(student_id, concept_id)
    result = [{
        "concept_id": concept["id"],
        "name": concept["name"],
        "accuracy": evidence["accuracy"],
        "attempt_count": evidence["attempts"],
        "status": evidence["status"],
    }]
    return {
        "grade": grade,
        "active": True,
        "status": "live_demo",
        "topic_id": class_info["topic_id"],
        "overall_progress": round(evidence["accuracy"], 1),
        "concept_progress": result,
    }


@router.get("/concepts/{concept_id}")
def concept_details(concept_id: int):
    row = fetch_one(
        """
        SELECT c.id AS concept_id, c.name AS concept_name,
               t.id AS topic_id, t.name AS topic_name,
               s.id AS subject_id, s.name AS subject_name
        FROM concepts c
        JOIN topics t ON t.id = c.topic_id
        JOIN subjects s ON s.id = t.subject_id
        WHERE c.id = ?
        """,
        (concept_id,),
    )
    if not row:
        raise HTTPException(404, detail={"error": "concept_not_found", "message": "Concept not found."})
    return dict(row)
