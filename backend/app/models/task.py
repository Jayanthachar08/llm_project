from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id", ondelete="SET NULL"), nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="assignment")  # assignment, examination, event, lab, project
    deadline = Column(DateTime(timezone=True), nullable=True)  # submission deadline
    event_date = Column(DateTime(timezone=True), nullable=True)  # examination or event date
    
    importance = Column(String(50), default="Normal", nullable=False)  # Normal, Important, Critical
    difficulty = Column(String(50), default="Medium", nullable=False)  # Easy, Medium, Difficult
    estimated_duration = Column(Float, default=2.0, nullable=False)  # in hours
    priority_score = Column(Float, default=50.0, nullable=False)  # 0 to 100
    
    status = Column(String(50), default="Not Started", nullable=False)  # Not Started, In Progress, Completed
    confirmation_status = Column(String(50), default="confirmed", nullable=False)  # pending, confirmed, rejected
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="tasks")
    announcement = relationship("Announcement", back_populates="tasks")
    subject = relationship("Subject", back_populates="tasks")
    study_sessions = relationship("StudySession", back_populates="task", cascade="all, delete-orphan")
    progress_records = relationship("TaskProgress", back_populates="task", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="task", cascade="all, delete-orphan")
