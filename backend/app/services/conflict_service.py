from datetime import datetime, date, time, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.task import Task
from backend.app.models.study_session import StudySession
from backend.app.models.college_schedule import CollegeSchedule
from backend.app.models.availability import StudentAvailability
from backend.app.schemas.dashboard import ConflictItem

class ConflictService:
    @staticmethod
    def _parse_time(t_str: str) -> time:
        parts = t_str.strip().split(":")
        return time(int(parts[0]), int(parts[1]))

    @classmethod
    def detect_conflicts(cls, user_id: int, db: Session) -> List[ConflictItem]:
        """
        Detect all academic and study schedule conflicts for a given student:
        1. Study session overlaps
        2. Competing deadlines (same or adjacent day deadlines with high combined workload)
        3. Insufficient preparation time (workload > available study hours before deadline)
        4. College hours conflict (study session during college classes/hours)
        5. Outside student availability (study session when student is unavailable)
        """
        conflicts: List[ConflictItem] = []

        # Retrieve active data
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status != "Completed",
            Task.confirmation_status == "confirmed"
        ).all()

        sessions = db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.status == "scheduled"
        ).all()

        college_schedules = db.query(CollegeSchedule).filter(
            CollegeSchedule.user_id == user_id
        ).all()

        availabilities = db.query(StudentAvailability).filter(
            StudentAvailability.user_id == user_id
        ).all()

        # 1. Study Session Overlaps
        session_by_date: Dict[date, List[StudySession]] = {}
        for s in sessions:
            session_by_date.setdefault(s.session_date, []).append(s)

        for s_date, date_sessions in session_by_date.items():
            for i in range(len(date_sessions)):
                for j in range(i + 1, len(date_sessions)):
                    s1 = date_sessions[i]
                    s2 = date_sessions[j]
                    t1_start = cls._parse_time(s1.start_time)
                    t1_end = cls._parse_time(s1.end_time)
                    t2_start = cls._parse_time(s2.start_time)
                    t2_end = cls._parse_time(s2.end_time)

                    # Check overlap: start1 < end2 and start2 < end1
                    if t1_start < t2_end and t2_start < t1_end:
                        t1_title = s1.task.title if s1.task else f"Task #{s1.task_id}"
                        t2_title = s2.task.title if s2.task else f"Task #{s2.task_id}"
                        conflicts.append(
                            ConflictItem(
                                conflict_type="session_overlap",
                                severity="High",
                                title=f"Study Session Overlap on {s_date.strftime('%b %d')}",
                                description=(
                                    f"Session for '{t1_title}' ({s1.start_time}-{s1.end_time}) overlaps "
                                    f"with session for '{t2_title}' ({s2.start_time}-{s2.end_time})."
                                ),
                                task_ids=[s1.task_id, s2.task_id],
                                session_ids=[s1.id, s2.id],
                                suggested_action="Run the dynamic reschedule engine to re-align conflicting sessions."
                            )
                        )

        # 2. Competing Deadlines
        # Group tasks by target date (deadline or event date)
        deadlines_by_date: Dict[date, List[Task]] = {}
        for t in tasks:
            target_dt = t.deadline or t.event_date
            if target_dt:
                d = target_dt.date() if isinstance(target_dt, datetime) else target_dt
                deadlines_by_date.setdefault(d, []).append(t)

        for d_date, date_tasks in deadlines_by_date.items():
            if len(date_tasks) > 1:
                total_workload = sum(t.estimated_duration for t in date_tasks)
                task_names = ", ".join([f"'{t.title}' ({t.estimated_duration}h)" for t in date_tasks])
                conflicts.append(
                    ConflictItem(
                        conflict_type="competing_deadlines",
                        severity="High" if total_workload >= 5.0 else "Medium",
                        title=f"Competing Deadlines on {d_date.strftime('%b %d')}",
                        description=(
                            f"{len(date_tasks)} academic tasks are due on {d_date.strftime('%Y-%m-%d')}: {task_names}. "
                            f"Total estimated workload is {total_workload:.1f} hours."
                        ),
                        task_ids=[t.id for t in date_tasks],
                        suggested_action="Start high-priority preparation earlier to balance the heavy workload."
                    )
                )

        # 3. Insufficient Preparation Time
        # Calculate available study hours between now and each task's deadline
        now = datetime.now(timezone.utc)
        avail_map = {a.day_of_week: a for a in availabilities if a.is_available}

        for t in tasks:
            target_dt = t.deadline or t.event_date
            if not target_dt:
                continue

            # Ensure comparison datetimes are timezone aware
            if target_dt.tzinfo is None:
                target_dt = target_dt.replace(tzinfo=timezone.utc)

            if target_dt <= now:
                conflicts.append(
                    ConflictItem(
                        conflict_type="insufficient_time",
                        severity="High",
                        title=f"Overdue Task: '{t.title}'",
                        description=f"Task deadline {target_dt.strftime('%b %d, %H:%M')} has passed, but task is still pending.",
                        task_ids=[t.id],
                        suggested_action="Update task progress or mark completed."
                    )
                )
                continue

            # Calculate total available study hours until deadline
            total_available_hours = 0.0
            curr_day = now.date()
            end_day = target_dt.date()
            
            while curr_day <= end_day:
                day_name = curr_day.strftime("%A")
                if day_name in avail_map:
                    slot = avail_map[day_name]
                    s_time = cls._parse_time(slot.start_time)
                    e_time = cls._parse_time(slot.end_time)
                    slot_hours = (datetime.combine(curr_day, e_time) - datetime.combine(curr_day, s_time)).total_seconds() / 3600.0
                    total_available_hours += max(0.0, slot_hours)
                curr_day += timedelta(days=1)

            if total_available_hours < t.estimated_duration:
                conflicts.append(
                    ConflictItem(
                        conflict_type="insufficient_time",
                        severity="High",
                        title=f"Insufficient Study Time for '{t.title}'",
                        description=(
                            f"Task requires {t.estimated_duration:.1f} hours, but only {total_available_hours:.1f} hours "
                            f"of study availability exist before the deadline ({target_dt.strftime('%b %d')})."
                        ),
                        task_ids=[t.id],
                        suggested_action="Increase daily study availability or begin study immediately."
                    )
                )

        # 4. College Hours Conflict
        # Check if any study session falls within college hours on that weekday
        college_map = {c.day_of_week: c for c in college_schedules if c.day_of_week}
        for s in sessions:
            day_name = s.session_date.strftime("%A")
            if day_name in college_map:
                c_sched = college_map[day_name]
                c_start = cls._parse_time(c_sched.start_time)
                c_end = cls._parse_time(c_sched.end_time)
                s_start = cls._parse_time(s.start_time)
                s_end = cls._parse_time(s.end_time)

                if s_start < c_end and c_start < s_end:
                    t_title = s.task.title if s.task else f"Task #{s.task_id}"
                    conflicts.append(
                        ConflictItem(
                            conflict_type="college_hours",
                            severity="High",
                            title=f"College Hours Conflict on {day_name}",
                            description=(
                                f"Study session for '{t_title}' ({s.start_time}-{s.end_time}) collides with "
                                f"college hours ({c_sched.start_time}-{c_sched.end_time})."
                            ),
                            task_ids=[s.task_id],
                            session_ids=[s.id],
                            suggested_action="Reschedule study session outside college working hours."
                        )
                    )

        # 5. Outside Availability
        for s in sessions:
            day_name = s.session_date.strftime("%A")
            if day_name not in avail_map:
                t_title = s.task.title if s.task else f"Task #{s.task_id}"
                conflicts.append(
                    ConflictItem(
                        conflict_type="outside_availability",
                        severity="Medium",
                        title=f"Session Outside Available Days on {day_name}",
                        description=f"Study session for '{t_title}' is scheduled on a day not marked as available.",
                        task_ids=[s.task_id],
                        session_ids=[s.id],
                        suggested_action="Shift session to an active study day or update availability settings."
                    )
                )

        return conflicts

conflict_service = ConflictService()
