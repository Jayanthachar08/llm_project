from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class StudySessionBase(BaseModel):
    task_id: int
    session_date: date
    start_time: str = Field(..., description="HH:MM format, e.g. 18:00")
    end_time: str = Field(..., description="HH:MM format, e.g. 19:00")
    duration: float = Field(..., description="Duration in minutes")
    status: str = Field("scheduled", description="scheduled, completed, missed, cancelled")

class StudySessionCreate(StudySessionBase):
    pass

class StudySessionUpdate(BaseModel):
    status: Optional[str] = None
    session_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class StudySessionResponse(StudySessionBase):
    id: int
    user_id: int
    created_at: datetime
    task_title: Optional[str] = None
    task_category: Optional[str] = None
    subject_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
