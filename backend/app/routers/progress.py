from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.task import Task
from backend.app.models.subject import Subject
from backend.app.models.study_session import StudySession
from backend.app.schemas.dashboard import SubjectProgressItem
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/progress", tags=["Progress & Analytics"])

class ProgressSummaryResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    overdue_tasks: int
    completion_percentage: float
    study_hours_planned: float
    study_hours_completed: float

@router.get("/summary", response_model=ProgressSummaryResponse)
def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve high-level progress and study hour metrics for student."""
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.confirmation_status == "confirmed"
    ).all()

    now = datetime.now(timezone.utc)
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "Completed")
    in_progress_tasks = sum(1 for t in tasks if t.status == "In Progress")
    pending_tasks = sum(1 for t in tasks if t.status != "Completed")
    
    overdue_tasks = 0
    for t in tasks:
        if t.status != "Completed" and t.deadline:
            d = t.deadline
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            if d < now:
                overdue_tasks += 1

    completion_percentage = round((completed_tasks / total_tasks * 100.0), 1) if total_tasks > 0 else 0.0

    # Study sessions planned vs completed
    sessions = db.query(StudySession).filter(StudySession.user_id == current_user.id).all()
    planned_minutes = sum(s.duration for s in sessions)
    completed_minutes = sum(s.duration for s in sessions if s.status == "completed")

    return ProgressSummaryResponse(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        completion_percentage=completion_percentage,
        study_hours_planned=round(planned_minutes / 60.0, 1),
        study_hours_completed=round(completed_minutes / 60.0, 1)
    )

@router.get("/subjects", response_model=List[SubjectProgressItem])
def get_subject_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve subject-wise task completion analytics."""
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    result = []

    for s in subjects:
        subj_tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.subject_id == s.id,
            Task.confirmation_status == "confirmed"
        ).all()
        total = len(subj_tasks)
        completed = sum(1 for t in subj_tasks if t.status == "Completed")
        pct = round((completed / total * 100.0), 1) if total > 0 else 0.0
        result.append(SubjectProgressItem(
            subject_id=s.id,
            subject_name=s.subject_name,
            total_tasks=total,
            completed_tasks=completed,
            completion_percentage=pct
        ))

    # Also check unassigned subject tasks if any
    unassigned = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.subject_id.is_(None),
        Task.confirmation_status == "confirmed"
    ).all()
    if unassigned:
        total = len(unassigned)
        completed = sum(1 for t in unassigned if t.status == "Completed")
        pct = round((completed / total * 100.0), 1) if total > 0 else 0.0
        result.append(SubjectProgressItem(
            subject_id=None,
            subject_name="General / Unassigned",
            total_tasks=total,
            completed_tasks=completed,
            completion_percentage=pct
        ))

    return result
