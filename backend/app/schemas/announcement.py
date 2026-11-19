from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class AnnouncementCreate(BaseModel):
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    extracted_text: str = Field(..., min_length=1)
    source_type: str = Field(..., description="pdf, image, or text")

class AnnouncementResponse(BaseModel):
    id: int
    user_id: int
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    extracted_text: str
    source_type: str
    processing_status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
