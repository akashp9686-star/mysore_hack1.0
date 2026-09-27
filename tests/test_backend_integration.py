import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_student(client):
    r = client.get("/api/students/101")
    assert r.status_code == 200
    assert r.json()["id"] == 101


def test_progress(client):
    r = client.get("/api/students/102/progress")
    assert r.status_code == 200
    assert r.json()["weak_concepts"]
    assert r.json()["weak_concepts"][0]["status"] == "needs_intervention"
    assert r.json()["weak_concepts"][0]["likely_misconception"] == "Forgetting to divide by the coefficient of x."


def test_intervention(client):
    r = client.get("/api/students/102/intervention")
    assert r.status_code == 200
    body = r.json()
    assert body["concept_id"] == 2
    assert body["type"] == "targeted_practice"


def test_assessment(client):
    r = client.get("/api/assessments/2")
    assert r.status_code == 200
    assert r.json()["student_id"] == 102
    assert len(r.json()["questions"]) > 0


def test_teacher_matching_is_schema_safe(client):
    r = client.get("/api/teachers/match?concept_id=2")
    assert r.status_code == 200
    body = r.json()
    assert len(body["teachers"]) >= 1
    assert "matching_note" in body
    assert "expertise" not in body["teachers"][0]


def test_resources(client):
    r = client.get("/api/resources/2")
    assert r.status_code == 200
    assert len(r.json()["resources"]) >= 1


def test_facilitator(client):
    r = client.get("/api/facilitator/students")
    assert r.status_code == 200
    assert any(x["student_id"] == 102 for x in r.json()["students"])

def test_facilitator_student_surfaces_likely_misconception(client):
    from backend.database.seed import seed_database
    seed_database()
    r = client.get("/api/facilitator/students/102")
    assert r.status_code == 200
    assert r.json()["weak_concept"]["likely_misconception"] == "Forgetting to divide by the coefficient of x."


def test_all_40_questions_have_runtime_options(client):
    from backend.database.database import fetch_all
    from backend.database.seed import seed_database

    seed_database()
    concepts = fetch_all("SELECT id, topic_id FROM concepts ORDER BY id")
    seen = {}

    for concept in concepts:
        created = client.post(
            "/api/assessments",
            json={"student_id": 101, "topic_id": concept["topic_id"], "assessment_type": "diagnostic"},
        )
        assert created.status_code == 200
        assessment_id = created.json()["assessment_id"]
        detail = client.get(f"/api/assessments/{assessment_id}", params={"concept_id": concept["id"]})
        assert detail.status_code == 200
        for question in detail.json()["questions"]:
            seen[question["id"]] = len(question["options"])

    assert len(seen) == 40
    assert set(seen) == set(range(1, 11)) | set(range(101, 131))
    assert all(option_count == 4 for option_count in seen.values())
