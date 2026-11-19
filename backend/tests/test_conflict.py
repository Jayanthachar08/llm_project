from datetime import datetime, date, timedelta, timezone
from backend.app.models.user import User
from backend.app.models.task import Task
from backend.app.models.study_session import StudySession
from backend.app.models.availability import StudentAvailability
from backend.app.models.college_schedule import CollegeSchedule
from backend.app.services.conflict_service import conflict_service

def test_conflict_detection(db_session):
    # Setup user
    user = User(id=1, name="Test User", email="test@test.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    # 1. Test Session Overlap: DBMS 18:00-19:00 and CN 18:30-19:30
    task1 = Task(id=1, user_id=1, title="DBMS", category="assignment", status="Not Started", confirmation_status="confirmed", estimated_duration=2.0)
    task2 = Task(id=2, user_id=1, title="CN", category="assignment", status="Not Started", confirmation_status="confirmed", estimated_duration=2.0)
    db_session.add_all([task1, task2])
    db_session.commit()

    today = date.today()
    s1 = StudySession(user_id=1, task_id=1, session_date=today, start_time="18:00", end_time="19:00", duration=60, status="scheduled")
    s2 = StudySession(user_id=1, task_id=2, session_date=today, start_time="18:30", end_time="19:30", duration=60, status="scheduled")
    db_session.add_all([s1, s2])
    db_session.commit()

    conflicts = conflict_service.detect_conflicts(user_id=1, db=db_session)
    types = [c.conflict_type for c in conflicts]
    assert "session_overlap" in types

def test_competing_deadlines(db_session):
    user = User(id=1, name="Test User", email="test2@test.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    target_dt = datetime.now(timezone.utc) + timedelta(days=3)
    t1 = Task(id=1, user_id=1, title="DBMS Assignment", deadline=target_dt, estimated_duration=3.0, status="Not Started", confirmation_status="confirmed")
    t2 = Task(id=2, user_id=1, title="CN Assignment", deadline=target_dt, estimated_duration=3.0, status="Not Started", confirmation_status="confirmed")
    db_session.add_all([t1, t2])
    db_session.commit()

    conflicts = conflict_service.detect_conflicts(user_id=1, db=db_session)
    competing = [c for c in conflicts if c.conflict_type == "competing_deadlines"]
    assert len(competing) >= 1
    assert "Competing Deadlines" in competing[0].title
