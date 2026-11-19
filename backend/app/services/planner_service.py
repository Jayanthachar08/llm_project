import logging
from datetime import datetime, date, time, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.models.task import Task
from backend.app.models.study_session import StudySession
from backend.app.models.availability import StudentAvailability
from backend.app.models.college_schedule import CollegeSchedule
from backend.app.models.notification import Notification
from backend.app.services.priority_service import priority_service
from backend.app.schemas.study_session import StudySessionResponse

logger = logging.getLogger("campusflow.planner_service")

class PlannerService:
    DEFAULT_SESSION_MINUTES = 60
    DEFAULT_BREAK_MINUTES = 15
    DEFAULT_HORIZON_DAYS = 14

    @staticmethod
    def _parse_time(t_str: str) -> time:
        parts = t_str.strip().split(":")
        return time(int(parts[0]), int(parts[1]))

    @classmethod
    def generate_study_plan(
        cls,
        user_id: int,
        db: Session,
        session_duration: int = 60,
        break_duration: int = 15,
        horizon_days: int = 14,
        preserve_completed: bool = True
    ) -> Dict[str, Any]:
        """
        Generate deterministic personalized study timetable:
        1. Fetch uncompleted confirmed tasks.
        2. Recalculate priority scores (High priority first).
        3. Determine available time slots respecting student availability, college hours, and breaks.
        4. Distribute workload into sessions scheduled before task deadlines.
        5. Preserve completed sessions.
        6. Return generated sessions, stats, and any infeasibility warnings.
        """
        # Fetch confirmed uncompleted tasks
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status != "Completed",
            Task.confirmation_status == "confirmed"
        ).all()

        if not tasks:
            return {
                "message": "No pending tasks found. Add or confirm tasks to generate a study plan.",
                "sessions_generated": 0,
                "sessions": [],
                "warnings": []
            }

        # Recalculate and update priority score for each task
        for t in tasks:
            detail = priority_service.evaluate_task_priority(t)
            t.priority_score = detail.priority_score
        db.commit()

        # Sort tasks by priority score descending
        tasks.sort(key=lambda t: t.priority_score, reverse=True)

        # Retrieve availability & college schedule
        availabilities = db.query(StudentAvailability).filter(
            StudentAvailability.user_id == user_id,
            StudentAvailability.is_available == True
        ).all()

        college_schedules = db.query(CollegeSchedule).filter(
            CollegeSchedule.user_id == user_id
        ).all()

        # Retrieve completed sessions to preserve
        completed_sessions = []
        if preserve_completed:
            completed_sessions = db.query(StudySession).filter(
                StudySession.user_id == user_id,
                StudySession.status == "completed"
            ).all()

            # Remove previously scheduled (uncompleted) sessions to avoid duplication
            db.query(StudySession).filter(
                StudySession.user_id == user_id,
                StudySession.status == "scheduled"
            ).delete()
            db.commit()
        else:
            db.query(StudySession).filter(StudySession.user_id == user_id).delete()
            db.commit()

        # Map occupied time intervals per date from preserved completed sessions
        occupied_slots: Dict[date, List[Tuple[time, time]]] = {}
        for cs in completed_sessions:
            s_time = cls._parse_time(cs.start_time)
            e_time = cls._parse_time(cs.end_time)
            occupied_slots.setdefault(cs.session_date, []).append((s_time, e_time))

        # Build college hours map
        college_map = {cs.day_of_week: cs for cs in college_schedules if cs.day_of_week}
        avail_map = {a.day_of_week: a for a in availabilities}

        today = date.today()
        warnings: List[str] = []
        new_sessions: List[StudySession] = []

        # Generate candidate slots across horizon days
        # Each day has a list of available (start_time, end_time)
        daily_available_slots: Dict[date, List[Tuple[time, time]]] = {}

        for offset in range(horizon_days):
            current_day = today + timedelta(days=offset)
            day_name = current_day.strftime("%A")

            if day_name not in avail_map:
                continue

            avail = avail_map[day_name]
            slot_start = cls._parse_time(avail.start_time)
            slot_end = cls._parse_time(avail.end_time)

            # College hours collision prevention
            col_sched = college_map.get(day_name)
            col_start = cls._parse_time(col_sched.start_time) if col_sched else None
            col_end = cls._parse_time(col_sched.end_time) if col_sched else None

            # Subdivide available time into session blocks
            curr_cursor = datetime.combine(current_day, slot_start)
            end_boundary = datetime.combine(current_day, slot_end)

            while curr_cursor + timedelta(minutes=session_duration) <= end_boundary:
                cand_start = curr_cursor.time()
                cand_end = (curr_cursor + timedelta(minutes=session_duration)).time()

                # Check conflict with college hours
                collision = False
                if col_start and col_end:
                    if cand_start < col_end and col_start < cand_end:
                        collision = True

                # Check conflict with existing completed sessions
                if current_day in occupied_slots:
                    for (occ_start, occ_end) in occupied_slots[current_day]:
                        if cand_start < occ_end and occ_start < cand_end:
                            collision = True
                            break

                if not collision:
                    daily_available_slots.setdefault(current_day, []).append((cand_start, cand_end))

                # Advance cursor by session duration + break duration
                curr_cursor += timedelta(minutes=session_duration + break_duration)

        # Allocate slots task by task (High priority first)
        for task in tasks:
            # Remaining hours to schedule
            needed_minutes = int(task.estimated_duration * 60)
            target_dt = task.deadline or task.event_date
            deadline_date = target_dt.date() if target_dt else (today + timedelta(days=horizon_days))

            allocated_minutes = 0

            # Scan available days up to the task's deadline
            for offset in range(horizon_days):
                if allocated_minutes >= needed_minutes:
                    break

                current_day = today + timedelta(days=offset)
                if current_day > deadline_date:
                    # Do not schedule study session AFTER the task deadline!
                    break

                if current_day not in daily_available_slots or not daily_available_slots[current_day]:
                    continue

                # Take available slot
                cand_start, cand_end = daily_available_slots[current_day].pop(0)

                # Create study session record
                session = StudySession(
                    user_id=user_id,
                    task_id=task.id,
                    session_date=current_day,
                    start_time=cand_start.strftime("%H:%M"),
                    end_time=cand_end.strftime("%H:%M"),
                    duration=session_duration,
                    status="scheduled"
                )
                db.add(session)
                new_sessions.append(session)
                allocated_minutes += session_duration

            if allocated_minutes < needed_minutes:
                missing_hours = (needed_minutes - allocated_minutes) / 60.0
                warnings.append(
                    f"Task '{task.title}' has {missing_hours:.1f} unscheduled hours before its deadline "
                    f"({deadline_date.strftime('%Y-%m-%d')}). Consider extending daily study availability."
                )

        db.commit()

        # Generate notifications for upcoming sessions and deadlines
        cls._create_notifications(user_id, new_sessions, tasks, db)

        # Build response
        sessions_response = []
        for s in new_sessions:
            db.refresh(s)
            item = StudySessionResponse.model_validate(s)
            item.task_title = s.task.title if s.task else None
            item.task_category = s.task.category if s.task else None
            item.subject_name = s.task.subject.subject_name if (s.task and s.task.subject) else None
            sessions_response.append(item)

        return {
            "message": f"Successfully generated study plan with {len(new_sessions)} sessions.",
            "sessions_generated": len(new_sessions),
            "sessions": sessions_response,
            "warnings": warnings,
            "horizon_days": horizon_days
        }

    @classmethod
    def reschedule_task(cls, user_id: int, task_id: int, db: Session) -> Dict[str, Any]:
        """
        Dynamically reschedule study sessions for an affected/delayed task while
        preserving all completed sessions and other tasks.
        """
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            return {"error": "Task not found"}

        # Delete scheduled (pending) sessions for this specific task
        db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.task_id == task_id,
            StudySession.status == "scheduled"
        ).delete()
        db.commit()

        # Re-run planner preserving completed
        return cls.generate_study_plan(user_id, db, preserve_completed=True)

    @classmethod
    def _create_notifications(
        cls,
        user_id: int,
        new_sessions: List[StudySession],
        tasks: List[Task],
        db: Session
    ):
        """Create structured reminders and notifications for deadlines and study sessions."""
        now = datetime.now(timezone.utc)

        # 1. Study Session notifications
        for s in new_sessions[:10]:  # Cap notification creations
            session_dt = datetime.combine(s.session_date, cls._parse_time(s.start_time)).replace(tzinfo=timezone.utc)
            # Notification 30 mins before session
            remind_time = session_dt - timedelta(minutes=30)
            if remind_time > now:
                msg = f"Upcoming Study Session: '{s.task.title}' today at {s.start_time}."
                # Avoid duplicate reminder
                existing = db.query(Notification).filter(
                    Notification.user_id == user_id,
                    Notification.task_id == s.task_id,
                    Notification.notification_type == "session",
                    Notification.message == msg
                ).first()
                if not existing:
                    notif = Notification(
                        user_id=user_id,
                        task_id=s.task_id,
                        notification_type="session",
                        message=msg,
                        scheduled_at=remind_time,
                        status="pending"
                    )
                    db.add(notif)

        # 2. Deadline notifications
        for t in tasks:
            target_dt = t.deadline or t.event_date
            if not target_dt:
                continue

            if target_dt.tzinfo is None:
                target_dt = target_dt.replace(tzinfo=timezone.utc)

            # Reminder 24 hours before deadline
            remind_time = target_dt - timedelta(hours=24)
            if remind_time > now:
                msg = f"Deadline Alert: '{t.title}' is due tomorrow at {target_dt.strftime('%H:%M')}!"
                existing = db.query(Notification).filter(
                    Notification.user_id == user_id,
                    Notification.task_id == t.id,
                    Notification.notification_type == "deadline",
                    Notification.message == msg
                ).first()
                if not existing:
                    notif = Notification(
                        user_id=user_id,
                        task_id=t.id,
                        notification_type="deadline",
                        message=msg,
                        scheduled_at=remind_time,
                        status="pending"
                    )
                    db.add(notif)

        db.commit()

planner_service = PlannerService()
