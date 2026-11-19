from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class CollegeSchedule(Base):
    __tablename__ = "college_schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    day_of_week = Column(String(20), nullable=True)  # Monday, Tuesday, etc. (null if one-time date)
    start_time = Column(String(10), nullable=False)  # HH:MM e.g. "09:00"
    end_time = Column(String(10), nullable=False)    # HH:MM e.g. "16:00"
    event_date = Column(Date, nullable=True)         # for specific date events
    schedule_type = Column(String(50), default="college_hours", nullable=False)  # college_hours, class, lab, exam

    # Relationships
    user = relationship("User", back_populates="college_schedules")
