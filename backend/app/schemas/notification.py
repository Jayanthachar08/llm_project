from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class NotificationBase(BaseModel):
    task_id: Optional[int] = None
    notification_type: str  # deadline, session, conflict, overdue
    message: str
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, read

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)
