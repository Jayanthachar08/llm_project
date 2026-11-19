from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.task import Task
from backend.app.models.subject import Subject
from backend.app.models.task_progress import TaskProgress
from backend.app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskConfirmBatch, TaskPriorityDetail
)
from backend.app.schemas.task_progress import TaskProgressCreate, TaskProgressResponse
from backend.app.services.priority_service import priority_service
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["Academic Tasks"])

def _format_task_response(task: Task) -> TaskResponse:
    res = TaskResponse.model_validate(task)
    if task.subject:
        res.subject_name = task.subject.subject_name
    return res

@router.get("", response_model=List[TaskResponse])
def get_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    subject_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all confirmed academic tasks for student with optional filtering."""
    query = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.confirmation_status == "confirmed"
    )

    if status_filter:
        query = query.filter(Task.status == status_filter)
    if category:
        query = query.filter(Task.category == category)
    if subject_id:
        query = query.filter(Task.subject_id == subject_id)

    tasks = query.order_by(Task.deadline.asc().nullslast(), Task.priority_score.desc()).all()
    return [_format_task_response(t) for t in tasks]

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new academic task manually."""
    task = Task(
        user_id=current_user.id,
        title=task_in.title.strip(),
        description=task_in.description,
        category=task_in.category,
        deadline=task_in.deadline,
        event_date=task_in.event_date,
        importance=task_in.importance,
        difficulty=task_in.difficulty,
        estimated_duration=task_in.estimated_duration,
        subject_id=task_in.subject_id,
        announcement_id=task_in.announcement_id,
        status=task_in.status,
        confirmation_status="confirmed"
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Calculate initial priority score
    detail = priority_service.evaluate_task_priority(task)
    task.priority_score = detail.priority_score
    db.commit()
    db.refresh(task)

    return _format_task_response(task)

@router.post("/confirm", response_model=List[TaskResponse], status_code=status.HTTP_201_CREATED)
def confirm_extracted_tasks(
    payload: TaskConfirmBatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Student Review & Confirmation Step:
    Persist reviewed tasks extracted by Gemini into PostgreSQL database.
    """
    saved_tasks = []

    for item in payload.tasks:
        subject_id = None
        if item.subject_name and item.subject_name.strip():
            subj_name = item.subject_name.strip()
            subject = db.query(Subject).filter(
                Subject.user_id == current_user.id,
                Subject.subject_name.ilike(subj_name)
            ).first()
            if not subject:
                subject = Subject(user_id=current_user.id, subject_name=subj_name)
                db.add(subject)
                db.commit()
                db.refresh(subject)
            subject_id = subject.id

        task = Task(
            user_id=current_user.id,
            announcement_id=payload.announcement_id,
            subject_id=subject_id,
            title=item.title.strip(),
            description=item.description,
            category=item.category,
            deadline=item.deadline,
            event_date=item.event_date,
            importance=item.importance,
            difficulty=item.difficulty,
            estimated_duration=item.estimated_duration,
            status="Not Started",
            confirmation_status="confirmed"
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Compute priority
        detail = priority_service.evaluate_task_priority(task)
        task.priority_score = detail.priority_score
        db.commit()
        db.refresh(task)

        saved_tasks.append(_format_task_response(task))

    return saved_tasks

@router.get("/priorities", response_model=List[TaskPriorityDetail])
def get_task_priorities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all confirmed tasks ordered by priority score with detailed component explanations."""
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.confirmation_status == "confirmed",
        Task.status != "Completed"
    ).all()

    details = [priority_service.evaluate_task_priority(t) for t in tasks]
    details.sort(key=lambda d: d.priority_score, reverse=True)
    return details

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details for a single task."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return _format_task_response(task)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    update_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task details and recalculate priority."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(task, field, val)

    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)

    # Recalculate priority
    detail = priority_service.evaluate_task_priority(task)
    task.priority_score = detail.priority_score
    db.commit()
    db.refresh(task)

    return _format_task_response(task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None

@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an academic task as completed and update progress."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "Completed"
    task.updated_at = datetime.now(timezone.utc)

    # Record progress log
    progress = TaskProgress(
        task_id=task.id,
        user_id=current_user.id,
        progress_percentage=100.0,
        status="Completed",
        notes="Task completed by student."
    )
    db.add(progress)
    db.commit()
    db.refresh(task)
    return _format_task_response(task)

@router.patch("/{task_id}/progress", response_model=TaskProgressResponse)
def update_task_progress(
    task_id: int,
    progress_in: TaskProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task progress percentage and status."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = progress_in.status
    if progress_in.progress_percentage >= 100.0:
        task.status = "Completed"
    elif progress_in.progress_percentage > 0:
        task.status = "In Progress"
    task.updated_at = datetime.now(timezone.utc)

    record = TaskProgress(
        task_id=task.id,
        user_id=current_user.id,
        progress_percentage=progress_in.progress_percentage,
        status=task.status,
        notes=progress_in.notes
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
