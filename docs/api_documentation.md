# CampusFlow AI – API Documentation

All API endpoints are prefixed with `/api` and documented interactively at `/docs` (FastAPI Swagger UI).

---

## 1. Authentication (`/api/auth`)
- `POST /api/auth/register`: Register new student account (creates defaults for availability and college timetable).
- `POST /api/auth/login`: Authenticate with email/password; returns signed JWT Bearer token.
- `GET /api/auth/me`: Retrieve current student profile (Requires Bearer token).

## 2. Profile & Timetable (`/api/profile`)
- `GET /api/profile`: Retrieve profile, enrolled subjects, study availability, and college timetable.
- `PUT /api/profile`: Update basic profile info.
- `GET /api/profile/subjects`: List academic subjects.
- `POST /api/profile/subjects`: Add new subject.
- `DELETE /api/profile/subjects/{id}`: Delete subject.
- `GET /api/profile/availability`: Retrieve weekly study availability slots.
- `PUT /api/profile/availability`: Batch update weekly study hours.
- `GET /api/profile/college-schedule`: Retrieve college hours timetable.
- `PUT /api/profile/college-schedule`: Batch update college timetable.

## 3. Announcements & Extraction (`/api/announcements`)
- `POST /api/announcements/upload`: Upload PDF or image file (PyMuPDF / Tesseract OCR + optional auto-RAG).
- `POST /api/announcements/paste-text`: Save pasted announcement text.
- `POST /api/announcements/extract`: Process text through Google GenAI with RAG context and Guardrails.
- `GET /api/announcements`: List user announcements.
- `GET /api/announcements/{id}`: Retrieve announcement details.

## 4. RAG Knowledge Base (`/api/rag`)
- `POST /api/rag/ingest`: Chunk, embed, and store document in persistent ChromaDB.
- `POST /api/rag/search`: Semantic similarity search with user isolation and source attribution.
- `DELETE /api/rag/documents/{id}`: Delete document from vector collection and PostgreSQL.
- `POST /api/rag/reindex`: Rebuild all ChromaDB embeddings from PostgreSQL chunks.

## 5. Tasks & Deadlines (`/api/tasks`)
- `GET /api/tasks`: List confirmed tasks (supports filters: `status`, `category`, `subject_id`).
- `POST /api/tasks`: Create task manually.
- `POST /api/tasks/confirm`: Student confirmation of Gemini-extracted tasks.
- `GET /api/tasks/priorities`: Retrieve active tasks ordered by priority with formula breakdown.
- `GET /api/tasks/{id}`: Retrieve single task.
- `PUT /api/tasks/{id}`: Update task fields.
- `DELETE /api/tasks/{id}`: Delete task.
- `PATCH /api/tasks/{id}/complete`: Mark task as Completed and record progress log.
- `PATCH /api/tasks/{id}/progress`: Update task completion percentage and notes.

## 6. Study Planner & Conflicts (`/api/planner`)
- `POST /api/planner/generate`: Generate personalized priority-first study timetable.
- `POST /api/planner/reschedule`: Dynamically reschedule study sessions for an affected task.
- `GET /api/planner/conflicts`: Detect session overlaps, competing deadlines, and insufficient study time.
- `GET /api/planner/calendar`: Unified calendar events (study sessions, deadlines, exams).
- `PATCH /api/planner/sessions/{id}`: Update study session status (e.g. mark completed).

## 7. Notifications & Reminders (`/api/notifications`)
- `GET /api/notifications`: List all reminders and alerts.
- `PATCH /api/notifications/{id}/read`: Mark notification as read.
- `POST /api/notifications/read-all`: Mark all notifications as read.

## 8. Dashboard Summary (`/api/dashboard`)
- `GET /api/dashboard/summary`: Aggregated summary KPIs, high-priority tasks, today's sessions, active conflicts, and subject progress.
