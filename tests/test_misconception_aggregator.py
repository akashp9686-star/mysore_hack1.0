from backend.database.database import fetch_all
from backend.database.seed import seed_database
from backend.services.misconception_aggregator import most_frequent_misconception


def setup_function():
    seed_database()


def test_most_frequent_misconception_is_deterministic_and_student_scoped():
    result = most_frequent_misconception(102, 2, concept_id=2)
    assert result is not None
    assert result["description"] == "Forgetting to divide by the coefficient of x."
    assert result["frequency"] == 3

    other_student = most_frequent_misconception(103, 3, concept_id=2)
    assert other_student is not None
    assert other_student["description"] == "Forgetting to divide by the coefficient of x."
    assert other_student["frequency"] == 2


def test_aggregator_ignores_correct_answers_and_untagged_answers():
    result = most_frequent_misconception(101, 1, concept_id=2)
    assert result is None
