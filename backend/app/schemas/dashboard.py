from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.task import TaskResponse
from backend.app.schemas.study_session import StudySessionResponse

class SubjectProgressItem(BaseModel):
    subject_id: Optional[int] = None
    subject_name: str
    total_tasks: int
    completed_tasks: int
    completion_percentage: float

class ConflictItem(BaseModel):
    conflict_type: str  # session_overlap, competing_deadlines, insufficient_time, college_hours, outside_availability
    severity: str       # High, Medium, Warning
    title: str
    description: str
    task_ids: List[int] = []
    session_ids: List[int] = []
    suggested_action: str

class DashboardSummary(BaseModel):
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    completion_percentage: float
    high_priority_count: int
    upcoming_deadlines_count: int
    today_sessions_count: int
    active_conflicts_count: int
    high_priority_tasks: List[TaskResponse] = []
    today_sessions: List[StudySessionResponse] = []
    conflicts: List[ConflictItem] = []
    subject_progress: List[SubjectProgressItem] = []
