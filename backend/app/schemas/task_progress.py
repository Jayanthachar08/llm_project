from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class TaskProgressBase(BaseModel):
    progress_percentage: float = Field(0.0, ge=0.0, le=100.0)
    status: str = Field("Not Started", description="Not Started, In Progress, Completed")
    notes: Optional[str] = None

class TaskProgressCreate(TaskProgressBase):
    task_id: int

class TaskProgressUpdate(TaskProgressBase):
    pass

class TaskProgressResponse(TaskProgressBase):
    id: int
    task_id: int
    user_id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
