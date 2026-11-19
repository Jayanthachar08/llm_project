# CampusFlow AI – Requirements Traceability Matrix (RTM)

## Project Identity
- **Project Title:** CampusFlow AI: An LLM-Powered Academic Task Planning and Deadline Management System
- **Project Description:** CampusFlow AI is an LLM-powered system that converts academic announcements, assignments, and schedules into organized tasks. It identifies deadlines, prioritizes tasks, detects scheduling conflicts, and generates personalized study plans. It also provides reminders, progress tracking, and dynamic schedule updates, helping students manage responsibilities and avoid missed deadlines.
- **Primary LLM:** Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`) via `google-genai` SDK.

---

## 1. Eight Mandatory Functional Requirements (R1 – R8)

| Req # | Mandatory Functional Requirement | Frontend UI Page | API Endpoint | Backend Service | Database Table | Algorithm / Logic | Automated Test |
|:---:|---|---|---|---|---|---|---|
| **R1** | **Convert academic announcements, assignments and schedules into organized tasks** | `UploadAnnouncement.jsx`<br>`ExtractionReview.jsx`<br>`TaskManagement.jsx` | `POST /api/announcements/upload`<br>`POST /api/announcements/extract`<br>`POST /api/tasks/confirm` | `gemini_service.py`<br>`document_service.py`<br>`rag_service.py` | `announcements`<br>`tasks`<br>`document_chunks` | Gemini 3.5 Flash-Lite few-shot structured extraction + PyMuPDF/OCR parser | `tests/test_document_gemini.py`<br>`tests/test_e2e.py` |
| **R2** | **Identify submission deadlines, examination dates and event dates** | `ExtractionReview.jsx`<br>`CalendarView.jsx`<br>`TaskManagement.jsx` | `POST /api/announcements/extract`<br>`GET /api/tasks`<br>`GET /api/planner/calendar` | `gemini_service.py`<br>`guardrail_service.py` | `tasks` | Strict temporal separation: submission deadline vs examination/event date; ISO 8601 normalization | `tests/test_document_gemini.py`<br>`tests/test_guardrails.py` |
| **R3** | **Prioritize academic tasks using urgency, importance, difficulty and workload** | `PriorityView.jsx`<br>`Dashboard.jsx` | `GET /api/tasks/priorities` | `priority_service.py` | `tasks`<br>`subjects` | $$P = 0.40U + 0.25I + 0.20D + 0.15W$$ with exponential urgency decay $$U=e^{-0.15 \times \Delta t}$$ | `tests/test_priority.py`<br>`tests/test_audit_validation.py` |
| **R4** | **Detect scheduling conflicts and competing deadlines** | `ConflictAlerts.jsx`<br>`Dashboard.jsx` | `GET /api/planner/conflicts` | `conflict_service.py` | `tasks`<br>`study_sessions`<br>`college_schedules` | Temporal interval overlap detection, same-day deadline competition, college-hour collision checks | `tests/test_conflict.py`<br>`tests/test_audit_validation.py` |
| **R5** | **Generate personalized study plans using student availability and academic responsibilities** | `StudyPlanner.jsx`<br>`CalendarView.jsx` | `POST /api/planner/generate`<br>`GET /api/planner/calendar` | `planner_service.py` | `study_sessions`<br>`student_availability`<br>`college_schedules` | Priority-first bin-packing timetable allocator with break insertion and college-hour exclusion | `tests/test_planner.py`<br>`tests/test_e2e.py` |
| **R6** | **Provide reminders for upcoming deadlines and study sessions** | `Notifications.jsx`<br>`Dashboard.jsx` | `GET /api/notifications`<br>`PATCH /api/notifications/{id}/read` | `reminders.py` (APScheduler) | `notifications`<br>`tasks` | Time-window threshold trigger (3-day, 1-day, deadline-day, session alert) with deduplication | `tests/test_e2e.py`<br>`tests/test_routes.py` |
| **R7** | **Track student progress and task completion** | `ProgressTracking.jsx`<br>`Dashboard.jsx` | `GET /api/progress/summary`<br>`GET /api/progress/subjects`<br>`PATCH /api/tasks/{id}/complete` | `progress.py`<br>`tasks.py` | `task_progress`<br>`tasks` | Ratio completion calculation, planned vs completed study hours aggregation, subject KPI metrics | `tests/test_routes.py`<br>`tests/test_e2e.py` |
| **R8** | **Dynamically update schedules when tasks are added, completed, delayed or modified** | `StudyPlanner.jsx`<br>`ConflictAlerts.jsx` | `POST /api/planner/reschedule` | `planner_service.py` | `study_sessions`<br>`schedule_change_history` | Dynamic rescheduling preserving completed sessions, finding next feasible free slots | `tests/test_planner.py`<br>`tests/test_audit_validation.py` |

---

## 2. Technical Infrastructure Traceability

| Req # | Subsystem | Implementation Files | API Endpoints | Database Tables | Frontend UI Page | Test Verification |
|:---:|---|---|---|---|---|---|
| **SYS-1** | **User Registration, Login & JWT Auth** | `app/core/security.py`<br>`app/routers/auth.py` | `POST /api/auth/register`<br>`POST /api/auth/login`<br>`GET /api/auth/me` | `users` | `Login.jsx`<br>`Register.jsx` | `tests/test_auth.py`<br>`tests/test_e2e.py` |
| **SYS-2** | **Student Profile & Availability Setup** | `app/routers/profile.py`<br>`app/routers/availability.py`<br>`app/models/availability.py` | `GET /api/profile`<br>`PUT /api/profile`<br>`GET /api/availability`<br>`PUT /api/availability` | `student_availability`<br>`college_schedules` | `Profile.jsx`<br>`Settings.jsx` | `tests/test_routes.py`<br>`tests/test_e2e.py` |
| **SYS-3** | **Retrieval-Augmented Generation (RAG)** | `app/services/rag_service.py`<br>`app/routers/rag.py` | `POST /api/rag/ingest`<br>`POST /api/rag/search`<br>`DELETE /api/rag/documents/{id}` | `document_chunks` | `RAGKnowledge.jsx` | `tests/test_rag.py`<br>`tests/test_rag_demonstration.py` |
| **SYS-4** | **Four-Layer Guardrails** | `app/services/guardrail_service.py` | Layer 1 (Input), Layer 2 (Output), Layer 3 (Human-in-Loop), Layer 4 (Scheduling) | In-memory & schema validators | `ExtractionReview.jsx`<br>`UploadAnnouncement.jsx` | `tests/test_guardrails.py`<br>`tests/test_audit_validation.py` |
| **SYS-5** | **CAAD Dataset & LLM Benchmark Suite** | `dataset/announcements.json`<br>`dataset/evaluate_dataset.py`<br>`dataset/evaluate_prompts.py` | CLI benchmarks | Benchmark metrics | Evaluation report | `evaluate_dataset.py` (85.14% F1)<br>`evaluate_prompts.py` |
