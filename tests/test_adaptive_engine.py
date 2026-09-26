from backend.services.adaptive_engine import evaluate_student

def test_struggling_student():
    result=evaluate_student(102,2)
    assert result['status']=='needs_intervention'
    assert result['recommended_action'] in ('targeted_practice','teacher_session')
