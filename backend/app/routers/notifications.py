from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.notification import Notification
from backend.app.schemas.notification import NotificationResponse
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications & Reminders"])

@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all reminders and notifications for the authenticated student."""
    return db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.scheduled_at.desc()).all()

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.status = "read"
    db.commit()
    db.refresh(notif)
    return notif

@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all pending or sent notifications as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).update({"status": "read"})
    db.commit()
    return {"message": "All notifications marked as read."}
