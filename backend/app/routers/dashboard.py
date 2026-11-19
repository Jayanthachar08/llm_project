from datetime import date, datetime, timezone
from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.task import Task
from backend.app.models.subject import Subject
from backend.app.models.study_session import StudySession
from backend.app.schemas.dashboard import DashboardSummary, SubjectProgressItem
from backend.app.schemas.task import TaskResponse
from backend.app.schemas.study_session import StudySessionResponse
from backend.app.services.conflict_service import conflict_service
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Student Dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated summary data for student dashboard:
    - Task counts and completion percentage
    - High priority tasks
    - Today's study sessions
    - Active conflict alerts
    - Subject-wise progress breakdown
    """
    # All confirmed tasks
    all_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.confirmation_status == "confirmed"
    ).all()

    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t.status == "Completed")
    in_progress_tasks = sum(1 for t in all_tasks if t.status == "In Progress")
    pending_tasks = sum(1 for t in all_tasks if t.status != "Completed")

    completion_percentage = round((completed_tasks / total_tasks * 100.0), 1) if total_tasks > 0 else 0.0

    # High priority tasks (score >= 70 and not completed)
    high_priority = [t for t in all_tasks if t.status != "Completed" and (t.priority_score or 0) >= 70.0]
    high_priority.sort(key=lambda t: t.priority_score, reverse=True)

    # Upcoming deadlines within next 7 days
    now = datetime.now(timezone.utc)
    upcoming_count = 0
    for t in all_tasks:
        if t.status != "Completed":
            target_dt = t.deadline or t.event_date
            if target_dt:
                if target_dt.tzinfo is None:
                    target_dt = target_dt.replace(tzinfo=timezone.utc)
                diff = (target_dt - now).total_seconds() / 86400.0
                if 0 <= diff <= 7:
                    upcoming_count += 1

    # Today's study sessions
    today = date.today()
    today_sessions_records = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.session_date == today
    ).order_by(StudySession.start_time.asc()).all()

    today_sessions_formatted = []
    for s in today_sessions_records:
        item = StudySessionResponse.model_validate(s)
        item.task_title = s.task.title if s.task else None
        item.task_category = s.task.category if s.task else None
        item.subject_name = s.task.subject.subject_name if (s.task and s.task.subject) else None
        today_sessions_formatted.append(item)

    # Conflicts
    conflicts = conflict_service.detect_conflicts(current_user.id, db)

    # Subject-wise progress breakdown
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    subj_map: Dict[int, str] = {s.id: s.subject_name for s in subjects}

    subject_stats: Dict[int, Dict[str, Any]] = {}
    for s in subjects:
        subject_stats[s.id] = {
            "name": s.subject_name,
            "total": 0,
            "completed": 0
        }

    for t in all_tasks:
        if t.subject_id and t.subject_id in subject_stats:
            subject_stats[t.subject_id]["total"] += 1
            if t.status == "Completed":
                subject_stats[t.subject_id]["completed"] += 1

    subject_progress_list = []
    for s_id, stats in subject_stats.items():
        if stats["total"] > 0:
            pct = round(stats["completed"] / stats["total"] * 100.0, 1)
        else:
            pct = 0.0
        subject_progress_list.append(
            SubjectProgressItem(
                subject_id=s_id,
                subject_name=stats["name"],
                total_tasks=stats["total"],
                completed_tasks=stats["completed"],
                completion_percentage=pct
            )
        )

    # Format high priority task responses
    high_priority_formatted = []
    for t in high_priority[:5]:
        res = TaskResponse.model_validate(t)
        res.subject_name = t.subject.subject_name if t.subject else None
        high_priority_formatted.append(res)

    return DashboardSummary(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        pending_tasks=pending_tasks,
        completion_percentage=completion_percentage,
        high_priority_count=len(high_priority),
        upcoming_deadlines_count=upcoming_count,
        today_sessions_count=len(today_sessions_records),
        active_conflicts_count=len(conflicts),
        high_priority_tasks=high_priority_formatted,
        today_sessions=today_sessions_formatted,
        conflicts=conflicts,
        subject_progress=subject_progress_list
    )
