from fastapi import APIRouter, HTTPException

from backend.database.database import fetch_one, fetch_all
from backend.services.adaptive_engine import evaluate_student

router = APIRouter(prefix="/students", tags=["progress"])


@router.get("/{student_id}/progress")
def progress(student_id: int):
    student = fetch_one("SELECT id FROM students WHERE id = ?", (student_id,))
    if not student:
        raise HTTPException(404, detail={"error": "student_not_found", "message": f"Student with ID {student_id} was not found."})

    latest_assessment = fetch_one(
        """
        SELECT topic_id
        FROM assessments
        WHERE student_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (student_id,),
    )

    current_topic = None
    concepts = []
    if latest_assessment:
        topic = fetch_one("SELECT name FROM topics WHERE id = ?", (latest_assessment["topic_id"],))
        current_topic = topic["name"] if topic else None
        concepts = fetch_all(
            """
            SELECT id, name
            FROM concepts
            WHERE topic_id = ?
            ORDER BY id
            """,
            (latest_assessment["topic_id"],),
        )

    concept_progress = []
    weak_concepts = []
    for concept in concepts:
        result = evaluate_student(student_id, concept["id"])
        item = {
            "concept_id": concept["id"],
            "name": concept["name"],
            "accuracy": result["accuracy"],
            "attempt_count": result["attempts"],
            "status": result["status"],
        }
        concept_progress.append(item)
        if result["status"] == "needs_intervention":
            weak_concepts.append(item)

    overall = fetch_one(
        """
        SELECT COALESCE(AVG(accuracy), 0) AS overall_progress
        FROM student_progress
        WHERE student_id = ?
        """,
        (student_id,),
    )

    return {
        "student_id": student_id,
        "overall_progress": round(float(overall["overall_progress"]), 2),
        "current_topic": current_topic,
        "concept_progress": concept_progress,
        "weak_concepts": weak_concepts,
    }
