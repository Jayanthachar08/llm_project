from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class CollegeScheduleBase(BaseModel):
    title: str = Field(..., max_length=100)
    day_of_week: Optional[str] = Field(None, description="Monday, Tuesday, etc.")
    start_time: str = Field(..., description="HH:MM format, e.g. 09:00")
    end_time: str = Field(..., description="HH:MM format, e.g. 16:00")
    event_date: Optional[date] = None
    schedule_type: str = Field("college_hours", description="college_hours, class, lab, exam")

class CollegeScheduleCreate(CollegeScheduleBase):
    pass

class CollegeScheduleResponse(CollegeScheduleBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class CollegeScheduleBatchUpdate(BaseModel):
    schedules: List[CollegeScheduleCreate]
