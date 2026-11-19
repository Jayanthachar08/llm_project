from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field("assignment", description="assignment, examination, event, lab, project")
    deadline: Optional[datetime] = None
    event_date: Optional[datetime] = None
    importance: str = Field("Normal", description="Normal, Important, Critical")
    difficulty: str = Field("Medium", description="Easy, Medium, Difficult")
    estimated_duration: float = Field(2.0, ge=0.25, le=100.0, description="Hours")
    subject_id: Optional[int] = None
    announcement_id: Optional[int] = None
    status: str = Field("Not Started", description="Not Started, In Progress, Completed")
    confirmation_status: str = Field("confirmed", description="pending, confirmed, rejected")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    deadline: Optional[datetime] = None
    event_date: Optional[datetime] = None
    importance: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_duration: Optional[float] = None
    subject_id: Optional[int] = None
    status: Optional[str] = None
    confirmation_status: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    user_id: int
    announcement_id: Optional[int] = None
    subject_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    category: str
    deadline: Optional[datetime] = None
    event_date: Optional[datetime] = None
    importance: str
    difficulty: str
    estimated_duration: float
    priority_score: Optional[float] = 50.0
    status: str = "Not Started"
    confirmation_status: str = "confirmed"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    subject_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class TaskConfirmItem(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "assignment"
    deadline: Optional[datetime] = None
    event_date: Optional[datetime] = None
    importance: str = "Normal"
    difficulty: str = "Medium"
    estimated_duration: float = 2.0
    subject_name: Optional[str] = None
    announcement_id: Optional[int] = None

class TaskConfirmBatch(BaseModel):
    announcement_id: Optional[int] = None
    tasks: List[TaskConfirmItem]

class TaskPriorityDetail(BaseModel):
    task: TaskResponse
    urgency_score: float
    importance_score: float
    difficulty_score: float
    workload_score: float
    priority_score: float
    priority_level: str  # High, Medium, Low
    explanation: str
