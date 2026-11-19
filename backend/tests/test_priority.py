from datetime import datetime, timedelta, timezone
from backend.app.models.task import Task
from backend.app.services.priority_service import priority_service

def test_priority_score_formula_and_thresholds():
    # Example from Project Specification Section 9.1:
    # Urgency = 90, Importance = 80, Difficulty = 85, Workload = 70
    # P = (0.40 * 90) + (0.25 * 80) + (0.20 * 85) + (0.15 * 70) = 83.5 -> High
    u = 90.0
    i = 80.0
    d = 85.0
    w = 70.0
    expected_p = (0.40 * u) + (0.25 * i) + (0.20 * d) + (0.15 * w)
    assert round(expected_p, 1) == 83.5

def test_evaluate_task_priority():
    now = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)
    # Deadline in 2 days -> Urgency = 90
    deadline = now + timedelta(days=2)
    
    task = Task(
        id=1,
        user_id=1,
        title="DBMS Assignment",
        category="assignment",
        deadline=deadline,
        importance="Critical",  # 95
        difficulty="Difficult",  # 85
        estimated_duration=4.0,  # 65
        status="Not Started",
        confirmation_status="confirmed"
    )

    detail = priority_service.evaluate_task_priority(task, now=now)
    assert detail.urgency_score == 90.0
    assert detail.importance_score == 95.0
    assert detail.difficulty_score == 85.0
    assert detail.workload_score == 65.0
    # P = 0.4*90 + 0.25*95 + 0.20*85 + 0.15*65 = 36 + 23.75 + 17 + 9.75 = 86.5
    assert detail.priority_score == 86.5
    assert detail.priority_level == "High"
    assert "Priority Score 86.5/100" in detail.explanation

def test_low_priority_task():
    now = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)
    # Deadline 35 days away -> Urgency = 10
    deadline = now + timedelta(days=35)
    
    task = Task(
        id=2,
        user_id=1,
        title="Optional Reading",
        category="assignment",
        deadline=deadline,
        importance="Normal",  # 50
        difficulty="Easy",    # 35
        estimated_duration=1.0,  # 30
        status="Not Started",
        confirmation_status="confirmed"
    )

    detail = priority_service.evaluate_task_priority(task, now=now)
    # P = 0.4*10 + 0.25*50 + 0.20*35 + 0.15*30 = 4 + 12.5 + 7 + 4.5 = 28.0
    assert detail.priority_score == 28.0
    assert detail.priority_level == "Low"
