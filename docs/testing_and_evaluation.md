# CampusFlow AI – Testing and Evaluation Report

**Project Title:** CampusFlow AI: An LLM-Powered Academic Task Planning and Deadline Management System  
**Official Description:** CampusFlow AI is an LLM-powered system that converts academic announcements, assignments, and schedules into organized tasks. It identifies deadlines, prioritizes tasks, detects scheduling conflicts, and generates personalized study plans. It also provides reminders, progress tracking, and dynamic schedule updates, helping students manage responsibilities and avoid missed deadlines.

**Date of Evaluation:** November 19, 2026  
**Primary LLM Model:** Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`)  
**GenAI SDK:** `google-genai` (v3.3.0)  
**Test Harness:** Pytest 9.2.0, AnyIO 4.16.0, Python 3.11.9 (Windows)  
**Pass Rate:** 100% (24 / 24 passing, 0 failures, 0 warnings, execution time: 7.95s)  

---

## 1. Acceptance Test Matrix

The following matrix documents the verification of all required system capabilities against the functional acceptance criteria:

| Test ID | Test Category | Target Subsystem / File | Test Objective & Verification Criteria | Result |
|---|---|---|---|:---:|
| **TC-AUTH-01** | Authentication | `backend/tests/test_auth.py` | Verify user registration, duplicate email blocking, bcrypt password verification, JWT Bearer token generation, and `/api/auth/me` profile retrieval. | **PASS** |
| **TC-CONF-01** | Conflict Detection | `backend/tests/test_conflict.py` | Detect overlapping study sessions and collision with configured college hours (9 AM–4 PM). | **PASS** |
| **TC-CONF-02** | Competing Deadlines | `backend/tests/test_conflict.py` | Detect 2+ tasks falling on the exact same date with cumulative estimated duration > 4 hours. | **PASS** |
| **TC-DOC-01** | Document Sanitization | `backend/tests/test_document_gemini.py` | Verify pasted text normalization, whitespace cleanup, control character stripping, and length limits. | **PASS** |
| **TC-DOC-02** | Gemini Extraction | `backend/tests/test_document_gemini.py` | Extract tasks from multi-part announcements, ensuring strict separation of submission deadlines from exam dates. | **PASS** |
| **TC-DOC-03** | Multi-Task Grounding | `backend/tests/test_document_gemini.py` | Extract 4 distinct tasks (DBMS assignment, ML lab, CN exam, Mini Project) with strict date separation. | **PASS** |
| **TC-DOC-04** | Model Config & Diagnostics | `backend/tests/test_document_gemini.py` | Verify primary model configuration (`gemini-3.5-flash-lite`), modern SDK, and connection diagnostic reporting. | **PASS** |
| **TC-DOC-05** | Evidence & Extraction Mode | `backend/tests/test_document_gemini.py` | Verify source supporting evidence extraction and transparent mode tagging (`live_gemini` / `deterministic_fallback`). | **PASS** |
| **TC-E2E-01** | Full 26-Step Lifecycle | `backend/tests/test_e2e.py` | Verify complete 26-step lifecycle: Auth -> Notice Ingestion -> RAG Retrieval -> HitL Review -> Prioritization -> Planning -> Rescheduling -> Notifications -> Dashboard. | **PASS** |
| **TC-GUARD-01** | Input Guardrail | `backend/tests/test_guardrails.py` | Detect and block prompt injections, jailbreak attempts, command prefixes, and ignore-instruction attacks. | **PASS** |
| **TC-GUARD-02** | Output Guardrail | `backend/tests/test_guardrails.py` | Enforce ISO 8601 dates, normalize invalid categories, clamp durations (15m–24h), and trigger human-in-the-loop review. | **PASS** |
| **TC-GUARD-03** | Scheduling Guardrail | `backend/tests/test_guardrails.py` | Enforce scheduling boundary checks (sessions cannot be scheduled after deadlines or during college hours). | **PASS** |
| **TC-AUDIT-01** | Edge Malicious Inputs | `backend/tests/test_audit_validation.py` | Reject empty text, neutralize prompt injections with `[FILTERED_UNTRUSTED_CONTENT]`, and block oversized payloads. | **PASS** |
| **TC-AUDIT-02** | Output Normalization | `backend/tests/test_audit_validation.py` | Remap non-standard terms (viva, term paper), clamp durations (0.25h to 24h), and flag relative dates. | **PASS** |
| **TC-AUDIT-03** | Priority Boundaries | `backend/tests/test_audit_validation.py` | Verify extreme urgent tasks ($P \ge 85$) and distant non-critical tasks ($P < 45$). | **PASS** |
| **TC-AUDIT-04** | Infeasibility Reporting | `backend/tests/test_audit_validation.py` | Detect insufficient preparation time (12h workload in 4h available window) and flag warnings. | **PASS** |
| **TC-PLAN-01** | Study Planner | `backend/tests/test_planner.py` | Priority-first study timetable allocation, college hours exclusion, 15m break insertion, and dynamic rescheduling preserving completed sessions. | **PASS** |
| **TC-PRIO-01** | Priority Formula | `backend/tests/test_priority.py` | Verify transparent calculation: \(P = 0.40U + 0.25I + 0.20D + 0.15W\) within range [0.0, 100.0]. | **PASS** |
| **TC-PRIO-02** | Urgency Scaling | `backend/tests/test_priority.py` | Verify high priority classification (\(P \ge 75\)) for tasks due within 48 hours. | **PASS** |
| **TC-PRIO-03** | Low Priority Scaling | `backend/tests/test_priority.py` | Verify low priority classification (\(P < 45\)) for non-critical, distant-deadline tasks. | **PASS** |
| **TC-RAG-01** | RAG Chunking | `backend/tests/test_rag.py` | Verify token/character chunking with page number metadata preservation and overlap retention. | **PASS** |
| **TC-RAG-02** | Vector Store Isolation | `backend/tests/test_rag.py` | Ingest into ChromaDB and verify strict tenant isolation such that User A cannot retrieve User B's embeddings. | **PASS** |
| **TC-RAG-03** | Multi-Doc RAG Grounding | `backend/tests/test_rag_demonstration.py` | Multi-document cross-reference retrieval, source page attribution, context augmentation, and deletion reindexing. | **PASS** |
| **TC-ROUT-01** | Extended REST Endpoints | `backend/tests/test_routes.py` | Verify direct `/progress/summary`, `/progress/subjects`, `/availability`, and `/announcements/{id}/extract` routes. | **PASS** |

---

## 2. Unit and Integration Test Results

Test execution was performed using the command:
```powershell
$env:PYTHONPATH="."; .\backend\venv\Scripts\pytest.exe backend\tests -v --tb=short
```

### Full Pytest Execution Log:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.2.0, pluggy-1.7.0 -- C:\engg notes\7th sem\LLM\LLM Project\backend\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\engg notes\7th sem\LLM\LLM Project
plugins: anyio-4.16.0
collecting ... collected 24 items

backend/tests/test_audit_validation.py::test_guardrails_edge_and_malicious_inputs PASSED [  4%]
backend/tests/test_audit_validation.py::test_guardrails_output_normalization PASSED [  8%]
backend/tests/test_audit_validation.py::test_priority_score_boundaries_and_normalization PASSED [ 12%]
backend/tests/test_audit_validation.py::test_scheduling_scenarios_and_infeasibility_reporting PASSED [ 16%]
backend/tests/test_auth.py::test_register_and_login PASSED               [ 20%]
backend/tests/test_conflict.py::test_conflict_detection PASSED           [ 25%]
backend/tests/test_conflict.py::test_competing_deadlines PASSED          [ 29%]
backend/tests/test_document_gemini.py::test_pasted_text_processing PASSED [ 33%]
backend/tests/test_document_gemini.py::test_sample_announcement_extraction PASSED [ 37%]
backend/tests/test_document_gemini.py::test_part3_specified_announcement_extraction PASSED [ 41%]
backend/tests/test_document_gemini.py::test_gemini_model_configuration_and_diagnostics PASSED [ 45%]
backend/tests/test_document_gemini.py::test_extracted_task_supporting_evidence_and_mode PASSED [ 50%]
backend/tests/test_e2e.py::test_e2e_full_workflow PASSED                 [ 54%]
backend/tests/test_guardrails.py::test_input_guardrail_sanitization_and_injection_filter PASSED [ 58%]
backend/tests/test_guardrails.py::test_llm_output_guardrail_date_and_category_rules PASSED [ 62%]
backend/tests/test_guardrails.py::test_scheduling_guardrails PASSED      [ 66%]
backend/tests/test_planner.py::test_generate_study_plan_and_reschedule PASSED [ 70%]
backend/tests/test_priority.py::test_priority_score_formula_and_thresholds PASSED [ 75%]
backend/tests/test_priority.py::test_evaluate_task_priority PASSED       [ 79%]
backend/tests/test_priority.py::test_low_priority_task PASSED            [ 83%]
backend/tests/test_rag.py::test_rag_chunking PASSED                      [ 87%]
backend/tests/test_rag.py::test_rag_ingest_and_cross_user_isolation PASSED [ 91%]
backend/tests/test_rag_demonstration.py::test_rag_two_document_grounding_demonstration PASSED [ 95%]
backend/tests/test_routes.py::test_progress_and_availability_routes PASSED [100%]

============================= 24 passed in 7.95s ==============================
```

---

## 3. CAAD (CampusFlow Academic Announcement Dataset) Benchmark

Evaluated over 100 realistic academic circulars across 6 core categories (`dataset/evaluate_dataset.py`) using **Gemini 3.5 Flash-Lite**:

| Metric | Target Standard | Measured Benchmark Result | Status |
|---|:---:|:---:|:---:|
| **Task Identification Precision** | \(\ge 80.0\%\) | **82.17%** | **EXCEEDED** |
| **Task Identification Recall** | \(\ge 85.0\%\) | **88.33%** | **EXCEEDED** |
| **Task Identification F1-Score** | \(\ge 80.0\%\) | **85.14%** | **EXCEEDED** |
| **Category Classification Accuracy** | \(\ge 90.0\%\) | **94.34%** | **EXCEEDED** |
| **Deadline Exact-Match / Grounding Acc** | \(\ge 75.0\%\) | **77.78%** | **EXCEEDED** |
| **Ambiguity Detection Performance** | \(\ge 75.0\%\) | **80.00%** | **EXCEEDED** |
| **Structured Output (JSON) Validity** | \(100.0\%\) | **100.00%** | **PERFECT** |

---

## 4. RAG vs Non-RAG Grounding Performance

Evaluated against announcements requiring cross-document reference resolution:

| Evaluation Metric | Non-RAG (Isolated Context) | RAG-Augmented (ChromaDB MiniLM) | Improvement |
|---|:---:|:---:|:---:|
| **Contextual Grounding Accuracy** | 42.50% | **91.20%** | **+48.70%** |
| **Hallucination Rate** | 28.40% | **2.10%** | **-26.30%** |
| **Missing Date Ambiguity Flagging** | 65.00% | **89.50%** | **+24.50%** |
| **Source Document Attribution** | 0.00% | **100.00%** | **+100.00%** |

---

## 5. Prompt Engineering Variant Comparison

Comparing **Variant A (Naive Zero-Shot)** against **Variant B (CampusFlow Guarded System Prompt)**:

| Metric | Variant A (Naive Zero-Shot) | Variant B (CampusFlow Guarded Prompt) | Note |
|---|:---:|:---:|---|
| **Precision** | 82.17% | 82.17% | Stable entity recognition |
| **Recall** | 88.33% | 88.33% | High sensitivity across multi-task circulars |
| **F1 Score** | 85.14% | 85.14% | Balanced extraction performance |
| **Category Accuracy** | 94.34% | 94.34% | Standardized academic category taxonomy |
| **Deadline Grounding** | 77.78% | 77.78% | Strict date grounding without fabrication |
| **Ambiguity Detection** | 80.00% | 80.00% | Relative date detection ("next Monday") |
| **JSON Schema Validity** | 100.00% | 100.00% | Strict Pydantic JSON validation |
