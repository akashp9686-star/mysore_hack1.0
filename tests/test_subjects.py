from fastapi.testclient import TestClient

from backend.database.database import fetch_all
from backend.database.seed import seed_database
from backend.main import app

client = TestClient(app)


def setup_function():
    seed_database()


def test_integrated_subject_rows_are_real_database_rows():
    rows = fetch_all("SELECT id, name FROM subjects ORDER BY id")
    assert [(row["id"], row["name"]) for row in rows] == [
        (1, "Mathematics"),
        (2, "Science"),
        (3, "Social Science"),
        (4, "English"),
    ]


def test_subjects_endpoint_returns_all_subject_rows():
    response = client.get("/api/subjects")
    assert response.status_code == 200
    assert response.json()["subjects"] == [
        {"id": 1, "name": "Mathematics"},
        {"id": 2, "name": "Science"},
        {"id": 3, "name": "Social Science"},
        {"id": 4, "name": "English"},
    ]
