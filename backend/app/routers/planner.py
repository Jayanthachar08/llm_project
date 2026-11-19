from typing import List, Dict, Any, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.task import Task
from backend.app.models.study_session import StudySession
from backend.app.models.college_schedule import CollegeSchedule
from backend.app.schemas.study_session import StudySessionResponse, StudySessionUpdate
from backend.app.schemas.dashboard import ConflictItem
from backend.app.services.planner_service import planner_service
from backend.app.services.conflict_service import conflict_service
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/planner", tags=["Study Planner & Scheduling"])

class GeneratePlanRequest(BaseModel):
    session_duration: int = 60
    break_duration: int = 15
    horizon_days: int = 14
    preserve_completed: bool = True

class RescheduleRequest(BaseModel):
    task_id: int

class CalendarItem(BaseModel):
    id: str
    title: str
    event_type: str  # study_session, deadline, exam, college_hour
    start: str       # ISO format string or YYYY-MM-DDTHH:MM
    end: str
    category: Optional[str] = None
    subject: Optional[str] = None
    status: Optional[str] = None

@router.post("/generate")
def generate_study_plan(
    payload: GeneratePlanRequest = GeneratePlanRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized study timetable based on academic responsibilities,
    student availability, college hours, and priorities.
    """
    result = planner_service.generate_study_plan(
        user_id=current_user.id,
        db=db,
        session_duration=payload.session_duration,
        break_duration=payload.break_duration,
        horizon_days=payload.horizon_days,
        preserve_completed=payload.preserve_completed
    )
    return result

@router.post("/reschedule")
def reschedule_task(
    payload: RescheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dynamic Rescheduling Algorithm:
    Recalculates study sessions when a task is delayed or modified,
    preserving completed sessions and reporting infeasibilities.
    """
    result = planner_service.reschedule_task(
        user_id=current_user.id,
        task_id=payload.task_id,
        db=db
    )
    return result

@router.get("/conflicts", response_model=List[ConflictItem])
def get_conflicts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Conflict Detection Engine:
    Detects session overlaps, competing deadlines, insufficient prep time,
    college hours collisions, and outside-availability sessions.
    """
    return conflict_service.detect_conflicts(current_user.id, db)

@router.get("/calendar", response_model=List[CalendarItem])
def get_calendar_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve unified calendar events:
    - Study sessions
    - Task deadlines
    - Examination dates
    - Academic events
    """
    events: List[CalendarItem] = []

    # 1. Study Sessions
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    ).all()

    for s in sessions:
        task_title = s.task.title if s.task else "Study Session"
        subj_name = s.task.subject.subject_name if (s.task and s.task.subject) else None
        events.append(
            CalendarItem(
                id=f"session-{s.id}",
                title=f"Study: {task_title}",
                event_type="study_session",
                start=f"{s.session_date.isoformat()}T{s.start_time}:00",
                end=f"{s.session_date.isoformat()}T{s.end_time}:00",
                category="study_session",
                subject=subj_name,
                status=s.status
            )
        )

    # 2. Task Deadlines and Exam Dates
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.confirmation_status == "confirmed"
    ).all()

    for t in tasks:
        subj_name = t.subject.subject_name if t.subject else None
        if t.deadline:
            d_str = t.deadline.isoformat()
            events.append(
                CalendarItem(
                    id=f"deadline-{t.id}",
                    title=f"Due: {t.title}",
                    event_type="deadline",
                    start=d_str,
                    end=d_str,
                    category=t.category,
                    subject=subj_name,
                    status=t.status
                )
            )
        if t.event_date:
            e_str = t.event_date.isoformat()
            events.append(
                CalendarItem(
                    id=f"exam-{t.id}",
                    title=f"Exam/Event: {t.title}",
                    event_type="exam",
                    start=e_str,
                    end=e_str,
                    category=t.category,
                    subject=subj_name,
                    status=t.status
                )
            )

    return events

@router.patch("/sessions/{session_id}", response_model=StudySessionResponse)
def update_study_session(
    session_id: int,
    session_update: StudySessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update status of a study session (e.g. mark completed, missed, or reschedule)."""
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")

    if session_update.status:
        session.status = session_update.status
    if session_update.session_date:
        session.session_date = session_update.session_date
    if session_update.start_time:
        session.start_time = session_update.start_time
    if session_update.end_time:
        session.end_time = session_update.end_time

    db.commit()
    db.refresh(session)
    res = StudySessionResponse.model_validate(session)
    res.task_title = session.task.title if session.task else None
    res.task_category = session.task.category if session.task else None
    res.subject_name = session.task.subject.subject_name if (session.task and session.task.subject) else None
    return res
