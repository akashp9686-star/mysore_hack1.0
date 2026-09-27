"""Teacher-authoring service for step-based misconception-tagged MCQs."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from backend.database.database import get_db, fetch_one
from backend.services.wrong_option_engine import generate_wrong_answer

DEMO_CONCEPT_ID = 2
DEFAULT_DIFFICULTY = "medium"


def _normalize_steps(steps: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for raw in steps:
        step_number = int(raw.get("step_number", len(normalized) + 1))
        step_text = str(raw.get("step_text", "")).strip()
        if not step_text:
            raise ValueError(f"Step {step_number} must have step_text.")
        mistakes = raw.get("mistakes") or []
        normalized.append(
            {
                "step_number": step_number,
                "step_text": step_text,
                "mistakes": [
                    {
                        "mistake_description": str(item.get("mistake_description", "")).strip(),
                        # Internal seed data may provide a pre-generated answer so
                        # the demo seed remains deterministic. Teachers do not see
                        # or submit this field.
                        "wrong_step_text": str(item.get("wrong_step_text", "")).strip(),
                    }
                    for item in mistakes
                ],
            }
        )

    numbers = [step["step_number"] for step in normalized]
    if not normalized:
        raise ValueError("At least one solution step is required.")
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("Solution steps must be numbered consecutively starting at 1.")
    for step in normalized:
        for mistake in step["mistakes"]:
            if not mistake["mistake_description"]:
                raise ValueError("Every mistake must have a description.")
    return normalized


def _generated_option(
    *,
    question_text: str,
    correct_answer: str,
    steps: list[dict[str, Any]],
    step_number: int,
    mistake: dict[str, Any],
) -> str:
    if mistake["wrong_step_text"]:
        return mistake["wrong_step_text"]
    return generate_wrong_answer(
        question_text=question_text,
        correct_answer=correct_answer,
        steps=steps,
        step_number=step_number,
        mistake_description=mistake["mistake_description"],
    )


def create_question_with_tagged_options(
    *,
    question_text: str,
    correct_answer: str,
    steps: Iterable[Mapping[str, Any]],
    teacher_id: int | None = None,
    concept_id: int = DEMO_CONCEPT_ID,
    difficulty: str = DEFAULT_DIFFICULTY,
    question_id: int | None = None,
) -> dict[str, Any]:
    """Create a question plus steps, misconceptions and generated DB options atomically."""
    question_text = str(question_text).strip()
    correct_answer = str(correct_answer).strip()
    if not question_text:
        raise ValueError("Question text is required.")
    if not correct_answer:
        raise ValueError("Correct answer is required.")

    normalized_steps = _normalize_steps(steps)

    concept = fetch_one(
        "SELECT id, topic_id, name FROM concepts WHERE id = ?",
        (concept_id,),
    )
    if not concept:
        raise ValueError(f"Concept {concept_id} was not found.")

    if teacher_id is not None:
        teacher = fetch_one("SELECT id FROM teachers WHERE id = ?", (teacher_id,))
        if not teacher:
            raise ValueError(f"Teacher {teacher_id} was not found.")

    created_option_ids: list[int] = []
    misconception_rows: list[dict[str, Any]] = []

    with get_db() as db:
        if question_id is None:
            question_cursor = db.execute(
                """
                INSERT INTO questions (concept_id, question_text, difficulty, correct_answer)
                VALUES (?, ?, ?, ?)
                """,
                (concept_id, question_text, difficulty, correct_answer),
            )
            stored_question_id = int(question_cursor.lastrowid)
        else:
            existing = db.execute(
                """
                SELECT id, concept_id, question_text, difficulty, correct_answer
                FROM questions WHERE id = ?
                """,
                (question_id,),
            ).fetchone()
            if not existing:
                raise ValueError(f"Question {question_id} was not found.")
            if int(existing["concept_id"]) != concept_id:
                raise ValueError("Existing question does not belong to the requested concept.")
            if existing["correct_answer"].strip().casefold() != correct_answer.casefold():
                raise ValueError("Existing question correct_answer does not match the authoring payload.")
            if existing["question_text"].strip() != question_text:
                raise ValueError("Existing question text does not match the authoring payload.")
            stored_question_id = int(existing["id"])

        for step in normalized_steps:
            db.execute(
                """
                INSERT INTO question_steps (question_id, step_number, step_text)
                VALUES (?, ?, ?)
                """,
                (stored_question_id, step["step_number"], step["step_text"]),
            )

        for step in normalized_steps:
            for mistake in step["mistakes"]:
                misconception = db.execute(
                    """
                    SELECT id, description, created_by_teacher_id
                    FROM misconceptions
                    WHERE concept_id = ? AND description = ?
                    ORDER BY id
                    LIMIT 1
                    """,
                    (concept_id, mistake["mistake_description"]),
                ).fetchone()
                if misconception is None:
                    cursor = db.execute(
                        """
                        INSERT INTO misconceptions (concept_id, description, created_by_teacher_id)
                        VALUES (?, ?, ?)
                        """,
                        (concept_id, mistake["mistake_description"], teacher_id),
                    )
                    misconception = db.execute(
                        """
                        SELECT id, description, created_by_teacher_id
                        FROM misconceptions WHERE id = ?
                        """,
                        (cursor.lastrowid,),
                    ).fetchone()
                misconception_rows.append(dict(misconception))

                option_text = _generated_option(
                    question_text=question_text,
                    correct_answer=correct_answer,
                    steps=normalized_steps,
                    step_number=step["step_number"],
                    mistake=mistake,
                )
                if option_text.strip().casefold() == correct_answer.casefold():
                    raise ValueError("The wrong-option engine generated the correct answer. Describe a more specific mistake.")

                # Do not duplicate the same option for the same question.
                duplicate = db.execute(
                    "SELECT id FROM question_options WHERE question_id = ? AND option_text = ? LIMIT 1",
                    (stored_question_id, option_text),
                ).fetchone()
                if duplicate is not None:
                    raise ValueError("The wrong-option engine generated a duplicate option. Describe a different mistake.")

                option_cursor = db.execute(
                    """
                    INSERT INTO question_options
                        (question_id, option_text, is_correct, misconception_id, deviates_at_step)
                    VALUES (?, ?, 0, ?, ?)
                    """,
                    (
                        stored_question_id,
                        option_text,
                        misconception["id"],
                        step["step_number"],
                    ),
                )
                created_option_ids.append(int(option_cursor.lastrowid))

        correct_cursor = db.execute(
            """
            INSERT INTO question_options
                (question_id, option_text, is_correct, misconception_id, deviates_at_step)
            VALUES (?, ?, 1, NULL, NULL)
            """,
            (stored_question_id, correct_answer),
        )
        correct_option_id = int(correct_cursor.lastrowid)

    return {
        "question_id": stored_question_id,
        "concept_id": concept_id,
        "topic_id": concept["topic_id"],
        "question_text": question_text,
        "difficulty": difficulty,
        "correct_answer": correct_answer,
        "step_count": len(normalized_steps),
        "wrong_option_ids": created_option_ids,
        "correct_option_id": correct_option_id,
        "misconceptions": misconception_rows,
    }
