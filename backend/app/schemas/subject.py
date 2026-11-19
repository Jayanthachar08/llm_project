from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class SubjectCreate(BaseModel):
    subject_name: str = Field(..., min_length=1, max_length=100)
    subject_code: Optional[str] = Field(None, max_length=20)

class SubjectResponse(BaseModel):
    id: int
    user_id: int
    subject_name: str
    subject_code: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
