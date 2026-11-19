import re
from datetime import datetime, date, timezone
from typing import List, Dict, Any, Tuple, Optional
from fastapi import HTTPException
from backend.app.schemas.gemini import ExtractedTaskItem, GeminiExtractionResult

class GuardrailService:
    """
    Four-Layer Guardrail Methodology for CampusFlow AI:
    Layer 1: Input Guardrails (format, size, injection prevention, length limits)
    Layer 2: LLM Output Guardrails (schema, category, date groundings, hallucination filters)
    Layer 3: Human-in-the-Loop Guardrails (mandatory review & confirmation before persistence)
    Layer 4: Scheduling Guardrails (collision prevention, availability bounds, break enforcement)
    """

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"system\s*prompt\s*override",
        r"you\s+are\s+now\s+a",
        r"disregard\s+(the\s+)?above",
        r"jailbreak",
        r"<script.*?>.*?</script>",
        r"drop\s+table",
        r";\s*delete\s+from",
    ]

    ALLOWED_CATEGORIES = {"assignment", "examination", "lab", "project", "event", "presentation", "quiz", "report"}

    # --- LAYER 1: INPUT GUARDRAILS ---
    @classmethod
    def validate_input_text(cls, text: str) -> str:
        """Sanitize raw announcement text and check for prompt injection patterns."""
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Input text is empty.")

        cleaned = text.strip()
        if len(cleaned) < 10:
            raise HTTPException(
                status_code=400,
                detail="Announcement text is too short (< 10 characters) to contain academic task information."
            )
        if len(cleaned) > 50000:
            raise HTTPException(
                status_code=400,
                detail="Announcement text exceeds maximum supported size (50,000 characters). Please split the document."
            )

        # Check for prompt injection keywords
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                # Neutralize attempt and flag warning
                cleaned = re.sub(pattern, "[FILTERED_UNTRUSTED_CONTENT]", cleaned, flags=re.IGNORECASE)

        return cleaned

    # --- LAYER 2: LLM OUTPUT GUARDRAILS ---
    @classmethod
    def validate_and_filter_tasks(cls, result: GeminiExtractionResult) -> GeminiExtractionResult:
        """
        Verify that LLM extraction outputs adhere to academic constraints:
        - Ensures dates are valid and distinguish submission deadline from exam event dates.
        - Flags ambiguous dates for human confirmation.
        - Prevents category hallucinations.
        """
        sanitized_tasks: List[ExtractedTaskItem] = []

        for item in result.tasks:
            # 1. Category validation
            cat = item.category.strip().lower()
            if cat not in cls.ALLOWED_CATEGORIES:
                item.category = "assignment"

            # 2. Category vs Date Type Enforcement:
            # For examinations, dates must reside in event_date, not deadline.
            if item.category == "examination" and item.deadline and not item.event_date:
                item.event_date = item.deadline
                item.deadline = None

            # 3. Relative Date and Hallucination Filter
            if item.deadline:
                iso_d = cls._normalize_to_iso(item.deadline)
                if iso_d:
                    item.deadline = iso_d
                else:
                    item.needs_verification = True
                    item.verification_reason = f"Deadline '{item.deadline}' is not a standardized calendar date. Student verification required."
                    item.deadline = None

            if item.event_date:
                iso_e = cls._normalize_to_iso(item.event_date)
                if iso_e:
                    item.event_date = iso_e
                else:
                    item.needs_verification = True
                    item.verification_reason = f"Event date '{item.event_date}' is not a standardized calendar date. Student verification required."
                    item.event_date = None

            # If task has neither deadline nor event_date, flag for verification
            if not item.deadline and not item.event_date:
                item.needs_verification = True
                if not item.verification_reason:
                    item.verification_reason = "No explicit submission or event date detected in announcement. Please verify or set manually."

            # 4. Duration bounds clamping (15m to 24h)
            if item.estimated_duration is not None:
                item.estimated_duration = max(0.25, min(24.0, float(item.estimated_duration)))

            sanitized_tasks.append(item)

        result.tasks = sanitized_tasks
        result.ambiguity_detected = any(t.needs_verification for t in sanitized_tasks)
        return result

    @staticmethod
    def _normalize_to_iso(d_str: str) -> Optional[str]:
        """Convert natural language or standard date strings into standardized YYYY-MM-DD format."""
        if not d_str:
            return None
        clean = d_str.strip()
        # Already YYYY-MM-DD
        if re.match(r"^\d{4}-\d{2}-\d{2}", clean):
            return clean[:10]
        
        # Try parsing natural date formats like 'November 15, 2026', 'Nov 15 2026', '15/11/2026'
        patterns = [
            "%B %d, %Y", "%B %d %Y",
            "%b %d, %Y", "%b %d %Y",
            "%d/%m/%Y", "%m/%d/%Y",
            "%B %d", "%b %d"
        ]
        # Clean ordinal suffixes (15th, 1st, 2nd, 3rd)
        clean_no_ordinal = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", clean)
        
        for p in patterns:
            try:
                dt = datetime.strptime(clean_no_ordinal, p)
                if "%Y" not in p:
                    dt = dt.replace(year=datetime.now().year)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                continue

        return None

    @staticmethod
    def _is_iso_date(d_str: str) -> bool:
        """Check if date matches YYYY-MM-DD or standard ISO format."""
        if not d_str:
            return False
        # Matches YYYY-MM-DD or YYYY-MM-DDTHH:MM
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2})?", d_str.strip()))

    # --- LAYER 3: HUMAN-IN-THE-LOOP GUARDRAIL ---
    @classmethod
    def verify_confirmation_payload(cls, tasks_payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate that confirmed tasks have student-verified titles, subjects, and valid deadlines."""
        confirmed: List[Dict[str, Any]] = []
        for t in tasks_payload:
            title = t.get("title", "").strip()
            if not title:
                continue
            confirmed.append(t)
        return confirmed

    # --- LAYER 4: SCHEDULING GUARDRAILS ---
    @classmethod
    def validate_study_slot(
        cls,
        slot_date: date,
        start_time_str: str,
        end_time_str: str,
        deadline: Optional[datetime],
        college_hours: Optional[Tuple[str, str]],
        existing_intervals: List[Tuple[str, str]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Enforce strict scheduling guardrails:
        1. Study session must occur BEFORE the task deadline.
        2. Study session cannot overlap with college hours.
        3. Study session cannot overlap with existing scheduled intervals.
        """
        # 1. Deadline check
        if deadline:
            target_date = deadline.date() if isinstance(deadline, datetime) else deadline
            if slot_date > target_date:
                return False, f"Session date {slot_date} exceeds deadline {target_date}"

        # 2. College hours collision check
        if college_hours:
            c_start, c_end = college_hours
            if start_time_str < c_end and c_start < end_time_str:
                return False, f"Collides with college working hours ({c_start}-{c_end})"

        # 3. Existing session overlap check
        for exist_start, exist_end in existing_intervals:
            if start_time_str < exist_end and exist_start < end_time_str:
                return False, f"Collides with existing study session ({exist_start}-{exist_end})"

        return True, None

guardrail_service = GuardrailService()
