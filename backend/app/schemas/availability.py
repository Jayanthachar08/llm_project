from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class AvailabilityBase(BaseModel):
    day_of_week: str = Field(..., description="Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday")
    start_time: str = Field(..., description="HH:MM format, e.g. 18:00")
    end_time: str = Field(..., description="HH:MM format, e.g. 22:00")
    is_available: bool = True

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityResponse(AvailabilityBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class AvailabilityBatchUpdate(BaseModel):
    availabilities: List[AvailabilityCreate]
