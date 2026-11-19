# CampusFlow AI – Four-Layer Guardrail Implementation

## Overview
To ensure system safety, data reliability, and zero hallucinated schedules, CampusFlow AI implements four distinct guardrail layers in `backend/app/services/guardrail_service.py`.

---

## Layer 1: Input Guardrails
- **File Type Restrictions:** Permits only `.pdf`, `.png`, `.jpg`, and `.jpeg`.
- **File Size Cap:** Enforces a maximum upload limit of 15MB.
- **Length Boundaries:** Rejects text shorter than 10 characters or exceeding 50,000 characters.
- **Prompt Injection Defense:** Regex scanning for prompt injection patterns (`ignore previous instructions`, `system prompt override`, `drop table`, `<script>`). Detected injections are sanitized to `[FILTERED_UNTRUSTED_CONTENT]`.

---

## Layer 2: LLM Output Guardrails
- **Pydantic Schema Validation:** Validates model response against `GeminiExtractionResult` and `ExtractedTaskItem`.
- **Date Separation Rule:** Enforces that examination/test dates are assigned to `event_date`, while assignments and projects receive `deadline`.
- **Date ISO Normalization:** Converts natural-language dates (e.g. "November 15, 2026") into ISO standard `2026-11-15`.
- **Relative Date Flagging:** Rejects relative ungrounded dates ("next Monday", "tomorrow") and sets `needs_verification = True`.

---

## Layer 3: Human-in-the-Loop Guardrails
- **Mandatory Review Interface (`/review`):** Gemini-extracted tasks are presented in a dedicated review page.
- **Student Ownership:** Students can edit titles, subjects, categories, deadlines, and durations, or reject false extractions before anything is committed to PostgreSQL.
- **Unconfirmed Task Persistence Guard:** Only tasks confirmed by the student are saved to the `tasks` table.

---

## Layer 4: Scheduling Guardrails
- **Deadline Boundary:** Rejects any study session scheduled after the task's deadline date.
- **College Hours Protection:** Prevents study sessions from overlapping with college hours (09:00 - 16:00).
- **Session Overlap Guard:** Prevents overlapping sessions and enforces a minimum 15-minute gap between study blocks.
- **Infeasibility Reporting:** Emits clear warnings if required study hours exceed available time before the deadline.
