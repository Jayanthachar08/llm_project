from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.availability import StudentAvailability
from backend.app.schemas.availability import AvailabilityResponse, AvailabilityBatchUpdate
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/availability", tags=["Student Availability"])

@router.get("", response_model=List[AvailabilityResponse])
def get_availabilities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly study availability slots."""
    return db.query(StudentAvailability).filter(StudentAvailability.user_id == current_user.id).all()

@router.put("", response_model=List[AvailabilityResponse])
def update_availabilities(
    data: AvailabilityBatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update weekly study availability slots."""
    db.query(StudentAvailability).filter(StudentAvailability.user_id == current_user.id).delete()
    new_slots = []
    for item in data.availabilities:
        slot = StudentAvailability(
            user_id=current_user.id,
            day_of_week=item.day_of_week,
            start_time=item.start_time,
            end_time=item.end_time,
            is_available=item.is_available
        )
        db.add(slot)
        new_slots.append(slot)
    db.commit()
    for s in new_slots:
        db.refresh(s)
    return new_slots
