from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class ScheduleChangeHistory(Base):
    __tablename__ = "schedule_change_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    change_type = Column(String(50), nullable=False)  # reschedule, delay, completion, manual_edit
    reason = Column(Text, nullable=False)
    previous_state = Column(Text, nullable=True)  # JSON or text description
    new_state = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User")
    task = relationship("Task")
