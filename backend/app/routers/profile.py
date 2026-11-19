from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.subject import Subject
from backend.app.models.availability import StudentAvailability
from backend.app.models.college_schedule import CollegeSchedule
from backend.app.schemas.user import UserResponse
from backend.app.schemas.subject import SubjectCreate, SubjectResponse
from backend.app.schemas.availability import AvailabilityCreate, AvailabilityResponse, AvailabilityBatchUpdate
from backend.app.schemas.college_schedule import CollegeScheduleCreate, CollegeScheduleResponse, CollegeScheduleBatchUpdate
from backend.app.core.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/profile", tags=["Profile & Preferences"])

class ProfileUpdate(BaseModel):
    name: Optional[str] = None

class FullProfileResponse(BaseModel):
    user: UserResponse
    subjects: List[SubjectResponse]
    availabilities: List[AvailabilityResponse]
    college_schedules: List[CollegeScheduleResponse]

@router.get("", response_model=FullProfileResponse)
def get_full_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full student profile, subjects, study availability, and college schedules."""
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    availabilities = db.query(StudentAvailability).filter(StudentAvailability.user_id == current_user.id).all()
    college_schedules = db.query(CollegeSchedule).filter(CollegeSchedule.user_id == current_user.id).all()

    return FullProfileResponse(
        user=UserResponse.model_validate(current_user),
        subjects=[SubjectResponse.model_validate(s) for s in subjects],
        availabilities=[AvailabilityResponse.model_validate(a) for a in availabilities],
        college_schedules=[CollegeScheduleResponse.model_validate(c) for c in college_schedules]
    )

@router.put("", response_model=UserResponse)
def update_profile(
    update_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update student basic information."""
    if update_data.name:
        current_user.name = update_data.name.strip()
        db.commit()
        db.refresh(current_user)
    return UserResponse.model_validate(current_user)

# Subjects management
@router.get("/subjects", response_model=List[SubjectResponse])
def get_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of student's academic subjects."""
    return db.query(Subject).filter(Subject.user_id == current_user.id).all()

@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_in: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new academic subject."""
    existing = db.query(Subject).filter(
        Subject.user_id == current_user.id,
        Subject.subject_name.ilike(subject_in.subject_name.strip())
    ).first()
    if existing:
        return existing
        
    subject = Subject(
        user_id=current_user.id,
        subject_name=subject_in.subject_name.strip(),
        subject_code=subject_in.subject_code.strip() if subject_in.subject_code else None
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an academic subject."""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()
    return None

# Availability management
@router.get("/availability", response_model=List[AvailabilityResponse])
def get_availabilities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly study availability slots."""
    return db.query(StudentAvailability).filter(StudentAvailability.user_id == current_user.id).all()

@router.put("/availability", response_model=List[AvailabilityResponse])
def update_availabilities(
    data: AvailabilityBatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update full weekly study availability slots."""
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

# College Schedules management
@router.get("/college-schedule", response_model=List[CollegeScheduleResponse])
def get_college_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get college working hours and classes."""
    return db.query(CollegeSchedule).filter(CollegeSchedule.user_id == current_user.id).all()

@router.put("/college-schedule", response_model=List[CollegeScheduleResponse])
def update_college_schedules(
    data: CollegeScheduleBatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update college working hours and schedules."""
    db.query(CollegeSchedule).filter(CollegeSchedule.user_id == current_user.id).delete()
    new_schedules = []
    for item in data.schedules:
        sched = CollegeSchedule(
            user_id=current_user.id,
            title=item.title,
            day_of_week=item.day_of_week,
            start_time=item.start_time,
            end_time=item.end_time,
            event_date=item.event_date,
            schedule_type=item.schedule_type
        )
        db.add(sched)
        new_schedules.append(sched)
    db.commit()
    for s in new_schedules:
        db.refresh(s)
    return new_schedules
