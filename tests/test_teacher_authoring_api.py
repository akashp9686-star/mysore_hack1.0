from fastapi.testclient import TestClient

from backend.database.database import fetch_one
from backend.database.seed import seed_database
from backend.main import app

client = TestClient(app)


def setup_function():
    seed_database()


def test_create_teacher_question_generates_tagged_wrong_option():
    response = client.post(
        "/api/teacher/questions",
        json={
            "teacher_id": 7,
            "question_text": "Solve: 6x - 4 = 3x + 11.",
            "correct_answer": "x = 5",
            "steps": [
                {"step_number": 1, "step_text": "6x - 4 = 3x + 11", "mistakes": []},
                {"step_number": 2, "step_text": "6x - 3x = 11 + 4", "mistakes": [
                    {"mistake_description": "Forgets to change the sign of the negative constant when transposing it."}
                ]},
                {"step_number": 3, "step_text": "3x = 15", "mistakes": [
                    {"mistake_description": "Forgets to divide by the coefficient of x."}
                ]},
                {"step_number": 4, "step_text": "x = 5", "mistakes": []},
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["question"]["concept_id"] == 2
    assert len(body["steps"]) == 4
    assert sum(1 for option in body["options"] if option["is_correct"]) == 1
    assert sum(1 for option in body["options"] if not option["is_correct"]) == 2
    assert any(option["option_text"] == "x = 15" for option in body["options"] if not option["is_correct"])

    question_id = body["question"]["id"]
    read = client.get(f"/api/teacher/questions/{question_id}")
    assert read.status_code == 200
    assert read.json()["question"]["question_text"] == "Solve: 6x - 4 = 3x + 11."


def test_teacher_created_question_appears_in_class_8_student_assessment():
    response = client.post(
        "/api/teacher/questions",
        json={
            "teacher_id": 7,
            "question_text": "Solve: 8x + 2 = 4x + 18.",
            "correct_answer": "x = 4",
            "steps": [
                {"step_number": 1, "step_text": "8x + 2 = 4x + 18", "mistakes": []},
                {"step_number": 2, "step_text": "8x - 4x = 18 - 2", "mistakes": [
                    {"mistake_description": "Forgets the sign change when moving the constant."}
                ]},
                {"step_number": 3, "step_text": "4x = 16", "mistakes": [
                    {"mistake_description": "Forgets to divide by the coefficient of x."}
                ]},
                {"step_number": 4, "step_text": "x = 4", "mistakes": []},
            ],
        },
    )
    assert response.status_code == 200
    question_id = response.json()["question"]["id"]

    created = client.post(
        "/api/assessments",
        json={"student_id": 101, "topic_id": 2, "assessment_type": "diagnostic"},
    )
    assert created.status_code == 200
    assessment_id = created.json()["assessment_id"]
    detail = client.get(f"/api/assessments/{assessment_id}", params={"concept_id": 2})
    assert detail.status_code == 200
    assert question_id in {q["id"] for q in detail.json()["questions"]}
    authored = next(q for q in detail.json()["questions"] if q["id"] == question_id)
    assert len(authored["options"]) == 3


def test_patch_regenerates_a_tagged_wrong_option_without_receiving_wrong_answer():
    read = client.get("/api/teacher/questions/3")
    assert read.status_code == 200
    existing = read.json()["steps"][1]["mistakes"][0]

    update = client.patch(
        "/api/teacher/questions/3/steps/2/mistakes",
        json={
            "option_id": existing["option_id"],
            "mistake_description": "Forgets the negative sign when transposing the constant.",
        },
    )
    assert update.status_code == 200
    assert update.json()["mistake"]["generated_wrong_answer"] != "x = 5"


def test_authoring_rejects_non_demo_concept():
    question = fetch_one("SELECT id FROM questions WHERE concept_id != 2 ORDER BY id LIMIT 1")
    if question is None:
        return
    response = client.get(f"/api/teacher/questions/{question['id']}")
    assert response.status_code == 400
