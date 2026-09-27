from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database.database import fetch_all, fetch_one, get_db
from backend.services.question_authoring import DEMO_CONCEPT_ID, create_question_with_tagged_options

router = APIRouter(prefix="/teacher", tags=["teacher-authoring"])


class MistakeInput(BaseModel):
    mistake_description: str = Field(min_length=1)


class StepInput(BaseModel):
    step_number: int = Field(ge=1)
    step_text: str = Field(min_length=1)
    mistakes: list[MistakeInput] = Field(default_factory=list)


class TeacherQuestionCreateRequest(BaseModel):
    question_text: str = Field(min_length=1)
    correct_answer: str = Field(min_length=1)
    steps: list[StepInput] = Field(min_length=1)
    teacher_id: int | None = Field(default=None, gt=0)


class MistakeUpdateRequest(BaseModel):
    mistake_description: str = Field(min_length=1)
    option_id: int | None = Field(default=None, gt=0)


def _require_demo_concept(question_id: int):
    question = fetch_one(
        """
        SELECT q.id, q.concept_id, q.question_text, q.difficulty, q.correct_answer,
               c.name AS concept_name, c.topic_id, t.name AS topic_name
        FROM questions q
        JOIN concepts c ON c.id = q.concept_id
        JOIN topics t ON t.id = c.topic_id
        WHERE q.id = ?
        """,
        (question_id,),
    )
    if not question:
        raise HTTPException(404, detail={"error": "question_not_found", "message": "Question not found."})
    if int(question["concept_id"]) != DEMO_CONCEPT_ID:
        raise HTTPException(
            400,
            detail={
                "error": "unsupported_authoring_scope",
                "message": "Teacher misconception authoring is currently scoped to Class 8 Algebra → Linear Equations → Variables on Both Sides.",
            },
        )
    return question


def _question_detail(question_id: int) -> dict:
    question = _require_demo_concept(question_id)
    steps = fetch_all(
        """
        SELECT id, step_number, step_text
        FROM question_steps
        WHERE question_id = ?
        ORDER BY step_number
        """,
        (question_id,),
    )
    option_rows = fetch_all(
        """
        SELECT qo.id, qo.option_text, qo.is_correct, qo.misconception_id,
               qo.deviates_at_step, m.description AS misconception_description
        FROM question_options qo
        LEFT JOIN misconceptions m ON m.id = qo.misconception_id
        WHERE qo.question_id = ?
        ORDER BY qo.id
        """,
        (question_id,),
    )

    mistakes_by_step: dict[int, list[dict]] = {int(step["step_number"]): [] for step in steps}
    options = []
    for row in option_rows:
        item = {
            "id": int(row["id"]),
            "option_text": row["option_text"],
            "is_correct": bool(row["is_correct"]),
            "misconception_id": int(row["misconception_id"]) if row["misconception_id"] is not None else None,
            "deviates_at_step": int(row["deviates_at_step"]) if row["deviates_at_step"] is not None else None,
            "misconception_description": row["misconception_description"],
        }
        options.append(item)
        if not item["is_correct"] and item["deviates_at_step"] in mistakes_by_step:
            mistakes_by_step[item["deviates_at_step"]].append(
                {
                    "option_id": item["id"],
                    "mistake_description": item["misconception_description"],
                    "generated_wrong_answer": item["option_text"],
                    "deviates_at_step": item["deviates_at_step"],
                    "misconception_id": item["misconception_id"],
                }
            )

    return {
        "question": {
            "id": int(question["id"]),
            "concept_id": int(question["concept_id"]),
            "concept_name": question["concept_name"],
            "topic_id": int(question["topic_id"]),
            "topic_name": question["topic_name"],
            "question_text": question["question_text"],
            "difficulty": question["difficulty"],
            "correct_answer": question["correct_answer"],
        },
        "steps": [
            {
                "id": int(step["id"]),
                "step_number": int(step["step_number"]),
                "step_text": step["step_text"],
                "mistakes": mistakes_by_step[int(step["step_number"])],
            }
            for step in steps
        ],
        "options": options,
    }


@router.post("/questions")
def create_teacher_question(payload: TeacherQuestionCreateRequest):
    try:
        result = create_question_with_tagged_options(
            question_text=payload.question_text,
            correct_answer=payload.correct_answer,
            steps=[step.model_dump() for step in payload.steps],
            teacher_id=payload.teacher_id,
            concept_id=DEMO_CONCEPT_ID,
        )
    except ValueError as exc:
        raise HTTPException(400, detail={"error": "invalid_question", "message": str(exc)}) from exc

    return _question_detail(int(result["question_id"]))


@router.get("/questions/{question_id}")
def get_teacher_question(question_id: int):
    return _question_detail(question_id)


@router.patch("/questions/{question_id}/steps/{step_number}/mistakes")
def update_teacher_mistake(question_id: int, step_number: int, payload: MistakeUpdateRequest):
    question = _require_demo_concept(question_id)
    step = fetch_one(
        "SELECT id, step_number, step_text FROM question_steps WHERE question_id = ? AND step_number = ?",
        (question_id, step_number),
    )
    if not step:
        raise HTTPException(404, detail={"error": "step_not_found", "message": "Solution step not found."})

    steps = fetch_all(
        "SELECT step_number, step_text FROM question_steps WHERE question_id = ? ORDER BY step_number",
        (question_id,),
    )

    from backend.services.wrong_option_engine import generate_wrong_answer

    try:
        generated = generate_wrong_answer(
            question_text=question["question_text"],
            correct_answer=question["correct_answer"],
            steps=steps,
            step_number=step_number,
            mistake_description=payload.mistake_description,
        )
    except ValueError as exc:
        raise HTTPException(400, detail={"error": "distractor_generation_failed", "message": str(exc)}) from exc

    with get_db() as db:
        misconception = db.execute(
            """
            SELECT id FROM misconceptions
            WHERE concept_id = ? AND description = ?
            ORDER BY id LIMIT 1
            """,
            (DEMO_CONCEPT_ID, payload.mistake_description.strip()),
        ).fetchone()
        if misconception is None:
            cursor = db.execute(
                """
                INSERT INTO misconceptions (concept_id, description)
                VALUES (?, ?)
                """,
                (DEMO_CONCEPT_ID, payload.mistake_description.strip()),
            )
            misconception = db.execute("SELECT id FROM misconceptions WHERE id = ?", (cursor.lastrowid,)).fetchone()

        if payload.option_id is not None:
            existing = db.execute(
                "SELECT id FROM question_options WHERE id = ? AND question_id = ? AND is_correct = 0",
                (payload.option_id, question_id),
            ).fetchone()
            if existing is None:
                raise HTTPException(404, detail={"error": "option_not_found", "message": "Tagged mistake option not found."})
            db.execute(
                """
                UPDATE question_options
                SET option_text = ?, misconception_id = ?, deviates_at_step = ?
                WHERE id = ? AND question_id = ? AND is_correct = 0
                """,
                (generated, misconception["id"], step_number, payload.option_id, question_id),
            )
            option_id = int(payload.option_id)
        else:
            duplicate = db.execute(
                "SELECT id FROM question_options WHERE question_id = ? AND option_text = ? LIMIT 1",
                (question_id, generated),
            ).fetchone()
            if duplicate is not None:
                raise HTTPException(400, detail={"error": "duplicate_option", "message": "The generated option already exists. Describe a different mistake."})
            cursor = db.execute(
                """
                INSERT INTO question_options
                    (question_id, option_text, is_correct, misconception_id, deviates_at_step)
                VALUES (?, ?, 0, ?, ?)
                """,
                (question_id, generated, misconception["id"], step_number),
            )
            option_id = int(cursor.lastrowid)

    refreshed = _question_detail(question_id)
    updated = next(
        (
            mistake
            for refreshed_step in refreshed["steps"]
            for mistake in refreshed_step["mistakes"]
            if mistake["option_id"] == option_id
        ),
        None,
    )
    return {
        "question_id": question_id,
        "step_number": step_number,
        "mistake": updated,
    }
