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
