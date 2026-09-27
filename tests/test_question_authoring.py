import pytest

from backend.database.database import fetch_all, fetch_one
from backend.database.seed import seed_database
from backend.services.question_authoring import create_question_with_tagged_options


def setup_function():
    seed_database()


def test_authoring_generates_wrong_options_from_teacher_mistakes():
    result = create_question_with_tagged_options(
        question_text="Solve: 7x - 5 = 2x + 20.",
        correct_answer="x = 5",
        teacher_id=7,
        steps=[
            {"step_number": 1, "step_text": "7x - 5 = 2x + 20", "mistakes": []},
            {
                "step_number": 2,
                "step_text": "7x - 2x = 20 + 5",
                "mistakes": [
                    {"mistake_description": "Forgets to change the negative sign when transposing the constant."},
                ],
            },
            {"step_number": 3, "step_text": "5x = 25", "mistakes": []},
            {"step_number": 4, "step_text": "x = 5", "mistakes": []},
        ],
    )

    assert result["concept_id"] == 2
    assert result["step_count"] == 4

    options = fetch_all(
        """
        SELECT option_text, is_correct, misconception_id, deviates_at_step
        FROM question_options WHERE question_id = ? ORDER BY id
        """,
        (result["question_id"],),
    )
    assert len(options) == 2
    assert sum(row["is_correct"] for row in options) == 1
    assert any(row["option_text"] == "x = 3" for row in options if not row["is_correct"])
    assert all(row["misconception_id"] is not None for row in options if not row["is_correct"])
    assert next(row for row in options if not row["is_correct"])["deviates_at_step"] == 2


def test_authoring_can_generate_division_mistake_without_teacher_entering_answer():
    result = create_question_with_tagged_options(
        question_text="Solve: 3x = 15.",
        correct_answer="x = 5",
        steps=[
            {"step_number": 1, "step_text": "3x = 15", "mistakes": [{"mistake_description": "Forgets to divide by the coefficient of x."}]},
            {"step_number": 2, "step_text": "x = 5", "mistakes": []},
        ],
    )
    wrong = fetch_one(
        "SELECT option_text FROM question_options WHERE question_id = ? AND is_correct = 0",
        (result["question_id"],),
    )
    assert wrong["option_text"] == "x = 15"


def test_authoring_rejects_non_consecutive_steps_before_inserting():
    with pytest.raises(ValueError, match="consecutively"):
        create_question_with_tagged_options(
            question_text="Solve x + 1 = 2.",
            correct_answer="x = 1",
            steps=[
                {"step_number": 1, "step_text": "x + 1 = 2", "mistakes": []},
                {"step_number": 3, "step_text": "x = 1", "mistakes": []},
            ],
        )

    question = fetch_one(
        "SELECT id FROM questions WHERE question_text = ?",
        ("Solve x + 1 = 2.",),
    )
    assert question is None


def test_selected_option_is_recorded_for_tagged_question():
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    assessment = client.post(
        "/api/assessments",
        json={"student_id": 103, "topic_id": 2, "assessment_type": "diagnostic"},
    )
    assert assessment.status_code == 200
    assessment_id = assessment.json()["assessment_id"]

    detail = client.get(f"/api/assessments/{assessment_id}", params={"concept_id": 2})
    assert detail.status_code == 200
    questions = detail.json()["questions"]
    assert len(questions) >= 4
    assert all(len(question["options"]) == 4 for question in questions[:4])

    answer = questions[0]["options"][0]
    response = client.post(
        f"/api/assessments/{assessment_id}/attempt",
        json={
            "student_id": 103,
            "question_id": questions[0]["id"],
            "answer": answer,
            "time_taken": 12,
        },
    )
    assert response.status_code == 200

    selected = fetch_one(
        "SELECT selected_option_id FROM attempts WHERE id = ?",
        (response.json()["attempt_id"],),
    )
    assert selected["selected_option_id"] is not None
