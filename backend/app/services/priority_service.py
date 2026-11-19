from datetime import datetime, timezone
from typing import Optional, Tuple
from backend.app.models.task import Task
from backend.app.schemas.task import TaskResponse, TaskPriorityDetail

class PriorityService:
    WEIGHT_URGENCY = 0.40
    WEIGHT_IMPORTANCE = 0.25
    WEIGHT_DIFFICULTY = 0.20
    WEIGHT_WORKLOAD = 0.15

    THRESHOLD_HIGH = 70.0
    THRESHOLD_MEDIUM = 40.0

    @classmethod
    def calculate_urgency_score(cls, target_date: Optional[datetime], now: Optional[datetime] = None) -> Tuple[float, str]:
        """
        Calculate dynamic urgency score based on remaining time until deadline or event date.
        Returns: (score [0-100], reason)
        """
        if not target_date:
            return 20.0, "No deadline or event date set (baseline urgency)"

        if now is None:
            now = datetime.now(timezone.utc)

        # Make sure both datetimes are timezone-aware or naive for consistent subtraction
        if target_date.tzinfo is None and now.tzinfo is not None:
            target_date = target_date.replace(tzinfo=timezone.utc)
        elif target_date.tzinfo is not None and now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        diff = target_date - now
        days_remaining = diff.total_seconds() / 86400.0

        if days_remaining <= 0:
            return 100.0, f"Overdue or due today ({abs(days_remaining):.1f} days passed/remaining)"
        elif days_remaining <= 1:
            return 95.0, f"Due within 24 hours ({days_remaining*24:.1f} hours left)"
        elif days_remaining <= 2:
            return 90.0, f"Due within 2 days ({days_remaining:.1f} days left)"
        elif days_remaining <= 3:
            return 80.0, f"Due within 3 days ({days_remaining:.1f} days left)"
        elif days_remaining <= 5:
            return 70.0, f"Due within 5 days ({days_remaining:.1f} days left)"
        elif days_remaining <= 7:
            return 55.0, f"Due within 1 week ({days_remaining:.1f} days left)"
        elif days_remaining <= 14:
            return 40.0, f"Due within 2 weeks ({days_remaining:.1f} days left)"
        elif days_remaining <= 30:
            return 25.0, f"Due within a month ({days_remaining:.1f} days left)"
        else:
            return 10.0, f"More than 30 days away ({days_remaining:.0f} days left)"

    @classmethod
    def calculate_importance_score(cls, importance: str) -> float:
        """Map importance string to 0-100 score."""
        val = (importance or "Normal").strip().capitalize()
        if val == "Critical":
            return 95.0
        elif val == "Important":
            return 75.0
        else:
            return 50.0

    @classmethod
    def calculate_difficulty_score(cls, difficulty: str) -> float:
        """Map difficulty string to 0-100 score."""
        val = (difficulty or "Medium").strip().capitalize()
        if val == "Difficult":
            return 85.0
        elif val == "Easy":
            return 35.0
        else:
            return 60.0

    @classmethod
    def calculate_workload_score(cls, estimated_hours: float) -> float:
        """Map estimated duration in hours to 0-100 workload score."""
        hours = max(0.25, estimated_hours or 2.0)
        if hours >= 10.0:
            return 95.0
        elif hours >= 6.0:
            return 80.0
        elif hours >= 4.0:
            return 65.0
        elif hours >= 2.0:
            return 50.0
        else:
            return 30.0

    @classmethod
    def evaluate_task_priority(cls, task: Task, now: Optional[datetime] = None) -> TaskPriorityDetail:
        """
        Evaluate full priority breakdown according to official algorithm:
        P = (0.40 * U) + (0.25 * I) + (0.20 * D) + (0.15 * W)
        """
        target_date = task.deadline or task.event_date
        urgency, urgency_desc = cls.calculate_urgency_score(target_date, now=now)
        importance = cls.calculate_importance_score(task.importance)
        difficulty = cls.calculate_difficulty_score(task.difficulty)
        workload = cls.calculate_workload_score(task.estimated_duration)

        priority_score = (
            (cls.WEIGHT_URGENCY * urgency) +
            (cls.WEIGHT_IMPORTANCE * importance) +
            (cls.WEIGHT_DIFFICULTY * difficulty) +
            (cls.WEIGHT_WORKLOAD * workload)
        )
        priority_score = round(priority_score, 2)

        if priority_score >= cls.THRESHOLD_HIGH:
            priority_level = "High"
        elif priority_score >= cls.THRESHOLD_MEDIUM:
            priority_level = "Medium"
        else:
            priority_level = "Low"

        date_label = "deadline" if task.deadline else ("event date" if task.event_date else "no fixed date")
        explanation = (
            f"Priority Score {priority_score}/100 ({priority_level}): "
            f"Urgency={urgency:.0f} ({urgency_desc}), "
            f"Importance={importance:.0f} ({task.importance}), "
            f"Difficulty={difficulty:.0f} ({task.difficulty}), "
            f"Workload={workload:.0f} ({task.estimated_duration}h required)."
        )

        task.priority_score = priority_score
        task_response = TaskResponse.model_validate(task)
        if task.subject:
            task_response.subject_name = task.subject.subject_name

        return TaskPriorityDetail(
            task=task_response,
            urgency_score=urgency,
            importance_score=importance,
            difficulty_score=difficulty,
            workload_score=workload,
            priority_score=priority_score,
            priority_level=priority_level,
            explanation=explanation
        )

    @classmethod
    def calculate_priority_score(cls, task: Task, now: Optional[datetime] = None) -> float:
        """Helper to calculate raw priority score scalar directly."""
        return cls.evaluate_task_priority(task, now=now).priority_score

priority_service = PriorityService()
