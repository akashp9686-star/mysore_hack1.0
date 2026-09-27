from backend.services.wrong_option_engine import generate_wrong_answer


def test_sign_mistake_generates_opposite_sign():
    assert generate_wrong_answer(
        question_text="Solve: 2x + 4 = x + 9.",
        correct_answer="x = 5",
        steps=[
            {"step_number": 1, "step_text": "2x + 4 = x + 9"},
            {"step_number": 2, "step_text": "2x - x = 9 - 4"},
        ],
        step_number=2,
        mistake_description="Forgets to change the negative sign when transposing the constant.",
    ) == "x = 13"


def test_division_mistake_uses_the_undivided_rhs():
    assert generate_wrong_answer(
        question_text="Solve: 4x = 20.",
        correct_answer="x = 5",
        steps=[{"step_number": 1, "step_text": "4x = 20"}],
        step_number=1,
        mistake_description="Forgets to divide by the coefficient of x.",
    ) == "x = 20"
