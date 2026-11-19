from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.availability import StudentAvailability
from backend.app.models.college_schedule import CollegeSchedule
from backend.app.schemas.user import UserRegister, UserLogin, UserResponse, Token
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

DEFAULT_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new student account."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    
    hashed = hash_password(user_in.password)
    user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize default student availability (6 PM - 10 PM on study days)
    for day in DEFAULT_DAYS:
        avail = StudentAvailability(
            user_id=user.id,
            day_of_week=day,
            start_time="18:00",
            end_time="22:00",
            is_available=True
        )
        db.add(avail)
    
    # Initialize default college schedule (9 AM - 4 PM Monday - Friday)
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        college_sched = CollegeSchedule(
            user_id=user.id,
            title="College Working Hours",
            day_of_week=day,
            start_time="09:00",
            end_time="16:00",
            schedule_type="college_hours"
        )
        db.add(college_sched)

    db.commit()

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=token, token_type="bearer", user=UserResponse.model_validate(user))

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate student and return JWT access token."""
    user = db.query(User).filter(User.email == credentials.email.lower().strip()).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=token, token_type="bearer", user=UserResponse.model_validate(user))

@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Retrieve profile of authenticated student."""
    return UserResponse.model_validate(current_user)
