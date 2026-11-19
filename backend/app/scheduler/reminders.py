import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from backend.app.database.connection import SessionLocal
from backend.app.models.notification import Notification
from backend.app.models.task import Task

logger = logging.getLogger("campusflow.scheduler")

scheduler = BackgroundScheduler()

def check_and_dispatch_reminders():
    """Background task to check pending reminders and trigger notifications."""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        # Find pending notifications whose scheduled time has arrived
        pending_notifications = db.query(Notification).filter(
            Notification.status == "pending",
            Notification.scheduled_at <= now
        ).all()

        for notif in pending_notifications:
            notif.status = "sent"
            notif.sent_at = now
            logger.info("Dispatched notification [%s] to user %d: %s", notif.notification_type, notif.user_id, notif.message)

        # Check for overdue tasks
        overdue_tasks = db.query(Task).filter(
            Task.status != "Completed",
            Task.confirmation_status == "confirmed",
            Task.deadline.isnot(None),
            Task.deadline < now
        ).all()

        for task in overdue_tasks:
            msg = f"OVERDUE ALERT: '{task.title}' was due on {task.deadline.strftime('%b %d, %H:%M')} and is incomplete!"
            existing = db.query(Notification).filter(
                Notification.user_id == task.user_id,
                Notification.task_id == task.id,
                Notification.notification_type == "overdue"
            ).first()

            if not existing:
                overdue_notif = Notification(
                    user_id=task.user_id,
                    task_id=task.id,
                    notification_type="overdue",
                    message=msg,
                    scheduled_at=now,
                    sent_at=now,
                    status="sent"
                )
                db.add(overdue_notif)
                logger.warning("Created overdue alert for user %d task '%s'", task.user_id, task.title)

        db.commit()
    except Exception as e:
        logger.error("Error in reminder dispatch cycle: %s", e)
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    """Start APScheduler in background."""
    if not scheduler.running:
        scheduler.add_job(
            check_and_dispatch_reminders,
            "interval",
            minutes=1,
            id="reminder_dispatch_job",
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler reminder service started.")

def shutdown_scheduler():
    """Shutdown APScheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler reminder service stopped.")
