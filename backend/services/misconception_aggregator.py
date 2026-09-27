"""Deterministic aggregation of teacher-tagged misconception evidence."""

from __future__ import annotations

from backend.database.database import fetch_one


def most_frequent_misconception(
    student_id: int,
    assessment_id: int,
    concept_id: int | None = None,
) -> dict[str, object] | None:
    """Return the most frequent teacher-tagged misconception for one student/assessment.

    When concept_id is supplied, the result is additionally constrained to that
    concept. Ties are broken deterministically by misconception id.
    """
    where = "a.student_id = ? AND a.assessment_id = ? AND a.is_correct = 0"
    params: list[object] = [student_id, assessment_id]
    if concept_id is not None:
        where += " AND m.concept_id = ?"
        params.append(concept_id)

    row = fetch_one(
        f"""
        SELECT m.id, m.description, COUNT(*) AS freq
        FROM attempts a
        JOIN question_options qo ON a.selected_option_id = qo.id
        JOIN misconceptions m ON qo.misconception_id = m.id
        WHERE {where}
        GROUP BY m.id, m.description
        ORDER BY freq DESC, m.id ASC
        LIMIT 1
        """,
        tuple(params),
    )
    if not row:
        return None
    return {
        "misconception_id": int(row["id"]),
        "description": row["description"],
        "frequency": int(row["freq"]),
    }
