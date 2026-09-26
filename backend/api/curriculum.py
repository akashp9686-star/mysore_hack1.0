from fastapi import APIRouter, HTTPException

from backend.database.database import fetch_all, fetch_one
from backend.services.adaptive_engine import evaluate_student

router = APIRouter(prefix="/curriculum", tags=["curriculum"])

MATH_CLASSES = {
    5: {
        "title": "Class 5 Mathematics",
        "topic_id": 10,
        "topics": ["Whole Numbers & Operations", "Fractions & Decimals", "Perimeter & Area"],
        "videos": [
            {"title": "Whole numbers basics", "query": "Class 5 maths whole numbers basics"},
            {"title": "Fractions & decimals basics", "query": "Class 5 maths fractions decimals basics"},
        ],
    },
    6: {
        "title": "Class 6 Mathematics",
        "topic_id": 11,
        "topics": ["Integers", "Fractions & Decimals", "Ratio & Proportion"],
        "videos": [
            {"title": "Integers basics", "query": "Class 6 maths integers basics"},
            {"title": "Ratio & proportion basics", "query": "Class 6 maths ratio proportion basics"},
        ],
    },
    7: {
        "title": "Class 7 Mathematics",
        "topic_id": 12,
        "topics": ["Rational Numbers", "Algebraic Expressions", "Simple Equations"],
        "videos": [
            {"title": "Rational numbers basics", "query": "Class 7 maths rational numbers basics"},
            {"title": "Algebra basics", "query": "Class 7 maths algebraic expressions basics"},
        ],
    },
    8: {
        "title": "Class 8 Mathematics",
        "topic_id": 13,
        "topics": ["Linear Equations", "Exponents & Powers", "Comparing Quantities"],
        "videos": [
            {"title": "Linear equations basics", "query": "Class 8 maths linear equations basics"},
            {"title": "Exponents & powers basics", "query": "Class 8 maths exponents powers basics"},
        ],
    },
    9: {
        "title": "Class 9 Mathematics",
        "topic_id": 14,
        "topics": ["Number Systems", "Polynomials", "Coordinate Geometry"],
        "videos": [
            {"title": "Number systems basics", "query": "Class 9 maths number systems basics"},
            {"title": "Polynomials basics", "query": "Class 9 maths polynomials basics"},
        ],
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

    topic_id = MATH_CLASSES[grade]["topic_id"]
    concepts = fetch_all("SELECT id, name FROM concepts WHERE topic_id = ? ORDER BY id", (topic_id,))
    result = []
    for concept in concepts:
        evidence = evaluate_student(student_id, concept["id"])
        result.append({
            "concept_id": concept["id"],
            "name": concept["name"],
            "accuracy": evidence["accuracy"],
            "attempt_count": evidence["attempts"],
            "status": evidence["status"],
        })

    overall = round(sum(x["accuracy"] for x in result) / len(result), 1) if result else 0
    return {
        "grade": grade,
        "topic_id": topic_id,
        "overall_progress": overall,
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
