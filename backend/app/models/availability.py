from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class StudentAvailability(Base):
    __tablename__ = "student_availability"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(String(20), nullable=False)  # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    start_time = Column(String(10), nullable=False)   # HH:MM e.g. "18:00"
    end_time = Column(String(10), nullable=False)     # HH:MM e.g. "22:00"
    is_available = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="availabilities")
