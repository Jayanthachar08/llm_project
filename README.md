# CampusFlow AI: An LLM-Powered Academic Task Planning and Deadline Management System

> **Official Project Description:**  
> CampusFlow AI is an LLM-powered system that converts academic announcements, assignments, and schedules into organized tasks. It identifies deadlines, prioritizes tasks, detects scheduling conflicts, and generates personalized study plans. It also provides reminders, progress tracking, and dynamic schedule updates, helping students manage responsibilities and avoid missed deadlines.

---

## 1. Project Overview

CampusFlow AI is an intelligent academic task planning and deadline management application developed as a final-year B.Tech LLM engineering project.

College students receive instructions and circulars through WhatsApp messages, PDFs, college portals, and examination schedules. Manually organizing this information, remembering competing deadlines, and scheduling study sessions around college working hours is challenging.

CampusFlow AI solves this by integrating:
1. **Google Gemini LLM (Modern `google-genai` SDK)** for natural-language announcement understanding and structured activity extraction.
2. **Retrieval-Augmented Generation (RAG)** with persistent **ChromaDB** vector storage and page-level source attribution.
3. **Four-Layer Guardrails** (Input sanitization, LLM output grounding, Human-in-the-Loop review, and Scheduling collision safeguards).
4. **Deterministic Python Engines** for numerical task prioritization, conflict detection, study plan generation, and dynamic rescheduling.
5. **Modern React SaaS Frontend** built with Vite, Tailwind CSS, Lucide React, and Recharts.

---

## 2. Core Functional Features

1. **Organized Academic Tasks**: Structured assignment, examination, lab, project, and event records.
2. **Deadline Identification**: Distinguishes submission deadlines from examination/event dates without fabrication.
3. **Task Prioritization Engine**: Numerical scoring using the official formula:
   $$\text{Priority Score } P = (0.40 \times U) + (0.25 \times I) + (0.20 \times D) + (0.15 \times W)$$
4. **Conflict Detection Engine**: Detects session overlaps, competing deadlines, insufficient prep time, and college hour clashes.
5. **Personalized Study Planner**: Priority-first scheduler that allocates 45/60/90-minute study blocks with mandatory breaks.
6. **Dynamic Rescheduling**: Recalculates affected study sessions when tasks are delayed, preserving all completed work.
7. **Automated Reminders**: Background APScheduler service generating deduplicated notifications.
8. **Academic Progress Tracking**: Real-time KPI cards, completion percentages, and subject workload charts.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 5, Tailwind CSS, React Router 6, Axios, Lucide React, Recharts |
| **Backend API** | Python 3.11, FastAPI, Uvicorn, Pydantic v2, Pydantic Settings |
| **LLM & AI** | Google GenAI SDK (`google-genai`), Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`) |
| **Vector DB / RAG** | ChromaDB (Persistent, cosine metric), all-MiniLM-L6-v2 embeddings |
| **Document Processing** | PyMuPDF (fitz), Pillow, Tesseract OCR |
| **Database & ORM** | PostgreSQL (Primary), SQLAlchemy 2.0, SQLite fallback for isolated tests |
| **Scheduler** | APScheduler (Background task dispatcher) |
| **Testing** | Pytest, HTTPX, StaticPool |

---

## 4. Architecture Data Flow

```mermaid
flowchart TD
    A["Student / Client"] --> B["React + Vite Frontend"]
    B --> C["FastAPI REST Backend"]
    C --> D["Document Service (PyMuPDF / OCR)"]
    D --> E["RAG Vector Pipeline (ChromaDB)"]
    E --> F["Google GenAI API (Gemini)"]
    F --> G["Four-Layer Guardrails"]
    G --> H["Human-in-the-Loop Review"]
    H --> I["PostgreSQL Database"]
    I --> J["Python Priority & Conflict Engines"]
    J --> K["Personalized Study Planner"]
    K --> L["APScheduler Reminder Service"]
    L --> B
```

---

## 5. Local Setup & Execution Guide (Windows)

### Prerequisites
- Python 3.11+
- Node.js v18+ and npm
- Windows PowerShell

### Step 1: Clone and Enter Repository
```powershell
cd "c:\engg notes\7th sem\LLM\LLM Project"
```

### Step 2: Configure Backend Environment
Create `backend/.env` (or copy from `backend/.env.example`):
```env
PROJECT_NAME="CampusFlow AI: An LLM-Powered Academic Task Planning and Deadline Management System"
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/campusflow_db
USE_SQLITE_FALLBACK=true
JWT_SECRET=campusflow_super_secret_jwt_key_academic_task_planner_2026
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

### Step 3: Run the Backend Development Server
```powershell
# In Terminal 1:
$env:PYTHONPATH="."
.\backend\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Swagger API Documentation: `http://127.0.0.1:8000/docs`
- Redoc API Documentation: `http://127.0.0.1:8000/redoc`

### Step 4: Run the Frontend Development Server
```powershell
# In Terminal 2:
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 6. Verification & Test Execution

### Run Full Pytest Suite (24 Tests, 100% Passing)
```powershell
$env:PYTHONPATH="."
.\backend\venv\Scripts\pytest.exe backend\tests -v --tb=short
```

### Run Prompt Engineering Benchmark Comparison
```powershell
$env:PYTHONPATH="."
.\backend\venv\Scripts\python.exe dataset\evaluate_prompts.py
```

### Run CAAD Academic Announcement Benchmark (100 Samples)
```powershell
$env:PYTHONPATH="."
.\backend\venv\Scripts\python.exe dataset\evaluate_dataset.py
```

### Benchmark Results
- **Task Identification Precision:** 82.17%
- **Task Identification Recall:** 88.33%
- **Task Identification F1-Score:** 85.14%
- **Category Classification Accuracy:** 94.34%
- **Deadline Exact-Match / Grounding Accuracy:** 77.78%
- **Ambiguity Detection Performance:** 80.00%
- **Structured Output (JSON) Validity:** 100.00%

---

## 7. Project Documentation Index

- [Project Overview](docs/project_overview.md)
- [Requirements Traceability Matrix](docs/requirements_traceability.md)
- [Development Status](docs/development_status.md)
- [System Architecture](docs/system_architecture.md)
- [Database Design](docs/database_design.md)
- [LLM Methodologies](docs/llm_methodologies.md)
- [Prompt Engineering](docs/prompt_engineering.md)
- [RAG Implementation](docs/rag_implementation.md)
- [Guardrail Implementation](docs/guardrail_implementation.md)
- [Algorithm Design](docs/algorithm_design.md)
- [API Documentation](docs/api_documentation.md)
- [Testing & Evaluation Report](docs/testing_and_evaluation.md)
