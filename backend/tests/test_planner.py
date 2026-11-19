from datetime import datetime, date, timedelta, timezone
from backend.app.models.user import User
from backend.app.models.task import Task
from backend.app.models.study_session import StudySession
from backend.app.models.availability import StudentAvailability
from backend.app.models.college_schedule import CollegeSchedule
from backend.app.services.planner_service import planner_service

def test_generate_study_plan_and_reschedule(db_session):
    user = User(id=1, name="Alex Student", email="alex@study.edu", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    # Add availability (Monday - Saturday, 18:00 - 22:00)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for d in days:
        avail = StudentAvailability(user_id=1, day_of_week=d, start_time="18:00", end_time="22:00", is_available=True)
        db_session.add(avail)
    db_session.commit()

    # Add college schedule (9 AM - 4 PM)
    for d in days:
        cs = CollegeSchedule(user_id=1, title="College", day_of_week=d, start_time="09:00", end_time="16:00")
        db_session.add(cs)
    db_session.commit()

    # Add 2 tasks: 1 high priority (due in 2 days), 1 normal priority (due in 7 days)
    now = datetime.now(timezone.utc)
    task_urgent = Task(
        user_id=1,
        title="Urgent AI Lab",
        category="lab",
        deadline=now + timedelta(days=2),
        importance="Critical",
        difficulty="Difficult",
        estimated_duration=2.0,  # 2 hours
        status="Not Started",
        confirmation_status="confirmed"
    )
    task_later = Task(
        user_id=1,
        title="DBMS Project",
        category="project",
        deadline=now + timedelta(days=7),
        importance="Normal",
        difficulty="Medium",
        estimated_duration=2.0,
        status="Not Started",
        confirmation_status="confirmed"
    )
    db_session.add_all([task_urgent, task_later])
    db_session.commit()

    # Generate plan
    result = planner_service.generate_study_plan(user_id=1, db=db_session)
    assert result["sessions_generated"] > 0
    sessions = db_session.query(StudySession).filter(StudySession.user_id == 1).all()
    assert len(sessions) >= 4  # 2h + 2h = 4 x 1-hour sessions

    # Mark first session as completed
    first_session = sessions[0]
    first_session.status = "completed"
    db_session.commit()

    # Test dynamic rescheduling: should preserve completed session!
    resched_result = planner_service.reschedule_task(user_id=1, task_id=task_urgent.id, db=db_session)
    preserved = db_session.query(StudySession).filter(
        StudySession.user_id == 1,
        StudySession.id == first_session.id
    ).first()
    assert preserved is not None
    assert preserved.status == "completed"
