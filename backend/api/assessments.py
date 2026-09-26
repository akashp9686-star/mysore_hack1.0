from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database.database import fetch_one, fetch_all, get_db, execute
from backend.services.adaptive_engine import database_status, evaluate_student
from backend.services.question_options import get_options
from backend.ai.ai_service import analyze_student_error

router = APIRouter(prefix="/assessments", tags=["assessments"])


ALLOWED_ASSESSMENT_TYPES = {"diagnostic", "practice", "targeted", "reassessment"}


class AssessmentCreateRequest(BaseModel):
    student_id: int = Field(gt=0)
    topic_id: int = Field(gt=0)
    assessment_type: str = Field(default="diagnostic")


class AttemptRequest(BaseModel):
    student_id: int = Field(gt=0)
    question_id: int = Field(gt=0)
    answer: str = Field(min_length=1)
    time_taken: int = Field(default=0, ge=0)


@router.post("")
def create_assessment(payload: AssessmentCreateRequest):
    if payload.assessment_type not in ALLOWED_ASSESSMENT_TYPES:
        raise HTTPException(400, detail={"error": "invalid_assessment_type", "message": "Unsupported assessment type."})
    if not fetch_one("SELECT id FROM students WHERE id = ?", (payload.student_id,)):
        raise HTTPException(404, detail={"error": "student_not_found", "message": "Student not found."})
    if not fetch_one("SELECT id FROM topics WHERE id = ?", (payload.topic_id,)):
        raise HTTPException(404, detail={"error": "topic_not_found", "message": "Topic not found."})
    assessment_id = execute(
        "INSERT INTO assessments(student_id, topic_id, assessment_type) VALUES (?, ?, ?)",
        (payload.student_id, payload.topic_id, payload.assessment_type),
    )
    return {"assessment_id": assessment_id, "student_id": payload.student_id, "topic_id": payload.topic_id, "assessment_type": payload.assessment_type}


@router.get("/{assessment_id}")
def get_assessment(assessment_id: int, concept_id: int | None = None):
    assessment = fetch_one(
        """
        SELECT id, student_id, topic_id, assessment_type, created_at
        FROM assessments WHERE id = ?
        """,
        (assessment_id,),
    )
    if not assessment:
        raise HTTPException(
            status_code=404,
            detail={"error": "assessment_not_found", "message": f"Assessment {assessment_id} was not found."},
        )

    if concept_id is not None:
        questions = fetch_all(
            """
            SELECT q.id, q.concept_id, q.question_text, q.difficulty
            FROM questions q
            JOIN concepts c ON c.id = q.concept_id
            WHERE c.topic_id = ? AND q.concept_id = ?
            ORDER BY q.id
            """,
            (assessment["topic_id"], concept_id),
        )
    else:
        questions = fetch_all(
            """
            SELECT q.id, q.concept_id, q.question_text, q.difficulty,
                   COALESCE((SELECT accuracy FROM student_progress sp
                             WHERE sp.student_id = ? AND sp.concept_id = q.concept_id), 0) AS accuracy,
                   COALESCE((SELECT attempt_count FROM student_progress sp
                             WHERE sp.student_id = ? AND sp.concept_id = q.concept_id), 0) AS concept_attempts
            FROM questions q
            JOIN concepts c ON c.id = q.concept_id
            WHERE c.topic_id = ?
            ORDER BY
                CASE WHEN COALESCE((SELECT accuracy FROM student_progress sp
                                    WHERE sp.student_id = ? AND sp.concept_id = q.concept_id), 0) < 50 THEN 0
                     WHEN COALESCE((SELECT accuracy FROM student_progress sp
                                    WHERE sp.student_id = ? AND sp.concept_id = q.concept_id), 0) < 80 THEN 1
                     ELSE 2 END,
                concept_attempts ASC,
                q.id
            LIMIT 6
            """,
            (assessment["student_id"], assessment["student_id"], assessment["topic_id"],
             assessment["student_id"], assessment["student_id"]),
        )

    # Avoid immediately repeating the learner's most recent questions when the
    # topic has enough alternatives. Targeted/reassessment flows still stay
    # scoped to their requested concept.
    if concept_id is None and len(questions) > 1:
        recent = fetch_all(
            """
            SELECT question_id FROM attempts
            WHERE student_id = ?
            ORDER BY id DESC LIMIT 6
            """,
            (assessment["student_id"],),
        )
        recent_ids = {int(row["question_id"]) for row in recent}
        fresh = [q for q in questions if int(q["id"]) not in recent_ids]
        if len(fresh) >= min(3, len(questions)):
            questions = fresh

    question_items = []
    for q in questions:
        item = dict(q)
        item["options"] = get_options(q["id"])
        item.pop("accuracy", None)
        item.pop("concept_attempts", None)
        question_items.append(item)
    topic = fetch_one("SELECT name FROM topics WHERE id = ?", (assessment["topic_id"],))
    return {**dict(assessment), "topic_name": topic["name"] if topic else None, "questions": question_items}


@router.post("/{assessment_id}/attempt")
def submit_attempt(assessment_id: int, payload: AttemptRequest):
    assessment = fetch_one("SELECT * FROM assessments WHERE id = ?", (assessment_id,))
    if not assessment:
        raise HTTPException(404, detail={"error": "assessment_not_found", "message": "Assessment not found."})

    if assessment["student_id"] != payload.student_id:
        raise HTTPException(
            400,
            detail={"error": "invalid_attempt", "message": "Student does not belong to this assessment."},
        )

    question = fetch_one("SELECT * FROM questions WHERE id = ?", (payload.question_id,))
    if not question:
        raise HTTPException(404, detail={"error": "question_not_found", "message": "Question not found."})

    # The question must belong to this assessment's topic.
    belongs = fetch_one(
        """
        SELECT 1
        FROM concepts c
        WHERE c.id = ? AND c.topic_id = ?
        """,
        (question["concept_id"], assessment["topic_id"]),
    )
    if not belongs:
        raise HTTPException(
            400,
            detail={"error": "invalid_attempt", "message": "Question does not belong to this assessment."},
        )

    correct = payload.answer.strip().casefold() == question["correct_answer"].strip().casefold()

    # Save the attempt first. The adaptive engine reads committed data, so the
    # decision is calculated immediately after this transaction.
    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO attempts
            (assessment_id, student_id, question_id, answer, is_correct, time_taken)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                assessment_id,
                payload.student_id,
                payload.question_id,
                payload.answer.strip(),
                int(correct),
                payload.time_taken,
            ),
        )
        attempt_id = cursor.lastrowid

    concept_id = question["concept_id"]
    adaptive = evaluate_student(payload.student_id, concept_id)

    concept_row = fetch_one("SELECT name FROM concepts WHERE id = ?", (concept_id,))
    ai_analysis = None
    if not correct:
        ai_analysis = analyze_student_error(
            question=question["question_text"],
            student_answer=payload.answer.strip(),
            correct_answer=question["correct_answer"],
            concept=concept_row["name"] if concept_row else "Mathematics concept",
        )

    def build_explanation(question_text: str, correct_answer: str, concept_name: str) -> str:
        text = (question_text or "").lower()
        if "perimeter of a square" in text:
            return f"A square has 4 equal sides, so perimeter = 4 × side. Here, 4 × 6 cm = {correct_answer}."
        if "area of a rectangle" in text:
            return f"Rectangle area = length × width. Here, 5 × 4 = {correct_answer}."
        if "percent" in text or "%" in text:
            return f"Convert the percentage to a decimal and multiply it by the given amount. The correct result is {correct_answer}."
        if text.startswith("simplify:"):
            return f"Combine like terms and keep any constant term unchanged. This gives {correct_answer}."
        if "ratio" in text:
            return f"Simplify the ratio by dividing both parts by their common factor. The result is {correct_answer}."
        if "coefficient" in text:
            return f"The coefficient is the number multiplying the variable. Here, it is {correct_answer}."
        if "x-coordinate" in text:
            return f"In an ordered pair (x, y), the first number is the x-coordinate. The correct answer is {correct_answer}."
        if "y-axis" in text:
            return f"A point on the y-axis has x = 0. The correct answer is {correct_answer}."
        if text.startswith("solve:"):
            return f"Isolate the variable by performing the same operation on both sides of the equation. The correct solution is {correct_answer}."
        return f"The correct answer is {correct_answer}. Review the {concept_name} concept and try a similar example."

    concept_name_value = concept_row["name"] if concept_row else "Mathematics concept"
    explanation = build_explanation(question["question_text"], question["correct_answer"], concept_name_value)

    progress = fetch_one(
        """
        SELECT COUNT(*) AS attempt_count
        FROM attempts
        WHERE student_id = ?
          AND question_id IN (SELECT id FROM questions WHERE concept_id = ?)
        """,
        (payload.student_id, concept_id),
    )

    # Keep the DB status within the shared enum. "practice" is represented by
    # the adaptive action, while the persisted status remains "normal".
    db_status = database_status(adaptive["status"])
    with get_db() as db:
        db.execute(
            """
            INSERT INTO student_progress
                (student_id, concept_id, accuracy, attempt_count, status, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(student_id, concept_id) DO UPDATE SET
                accuracy = excluded.accuracy,
                attempt_count = excluded.attempt_count,
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                payload.student_id,
                concept_id,
                adaptive["accuracy"],
                progress["attempt_count"],
                db_status,
            ),
        )

    return {
        "attempt_id": attempt_id,
        "correct": correct,
        "correct_answer": question["correct_answer"],
        "explanation": explanation,
        "concept_id": concept_id,
        "adaptive_result": {
            "student_id": payload.student_id,
            "concept_id": concept_id,
            "status": adaptive["status"],
            "recommended_action": adaptive["recommended_action"],
            "reason": adaptive["reason"],
            "teacher_required": adaptive["teacher_required"],
            "accuracy": adaptive["accuracy"],
            "ai_analysis": ai_analysis,
        },
    }
