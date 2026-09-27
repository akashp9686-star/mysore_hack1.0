from fastapi.testclient import TestClient

from backend.database.seed import seed_database
from backend.main import app

client = TestClient(app)


def setup_function():
    seed_database()


def test_only_class_8_is_live_in_math_curriculum():
    response = client.get('/api/curriculum/math/classes')
    assert response.status_code == 200
    classes = {row['grade']: row for row in response.json()['classes']}
    assert set(classes) == {5, 6, 7, 8, 9}
    assert classes[8]['active'] is True
    assert classes[8]['topic_id'] == 2
    assert classes[8]['concept_id'] == 2
    assert classes[8]['topics'] == ['Algebra', 'Linear Equations', 'Variables on Both Sides']
    assert all(classes[g]['active'] is False for g in (5, 6, 7, 9))
    assert all(classes[g]['topic_id'] is None for g in (5, 6, 7, 9))


def test_dummy_class_has_no_real_progress_questions():
    response = client.get('/api/curriculum/math/5/progress/101')
    assert response.status_code == 200
    body = response.json()
    assert body['active'] is False
    assert body['concept_progress'] == []


def test_class_8_student_assessment_is_scoped_to_variables_on_both_sides():
    created = client.post('/api/assessments', json={'student_id': 101, 'topic_id': 2, 'assessment_type': 'diagnostic'})
    assert created.status_code == 200
    assessment_id = created.json()['assessment_id']
    detail = client.get(f'/api/assessments/{assessment_id}', params={'concept_id': 2})
    assert detail.status_code == 200
    questions = detail.json()['questions']
    assert len(questions) >= 4
    assert all(question['concept_id'] == 2 for question in questions)
