from backend.app.services.document_service import document_service
from backend.app.services.gemini_service import gemini_service
from backend.app.schemas.gemini import GeminiExtractionResult

def test_pasted_text_processing():
    raw_text = "   Students must submit the AI assignment by Friday.   \n\n  "
    cleaned = document_service.process_pasted_text(raw_text)
    assert cleaned == "Students must submit the AI assignment by Friday."

def test_sample_announcement_extraction():
    announcement_text = (
        "Students must complete the DBMS assignment and submit it before November 15. "
        "The Computer Networks assignment is due on November 18. "
        "The DBMS internal examination will be conducted on November 19. "
        "Students should prepare all five modules."
    )
    result = gemini_service.extract_tasks_from_text(announcement_text)
    assert isinstance(result, GeminiExtractionResult)
    assert len(result.tasks) >= 3

    # Check that exam has category examination and assignment has assignment
    categories = [t.category for t in result.tasks]
    assert "assignment" in categories
    assert "examination" in categories

    # Verify event_date vs deadline separation
    exam_task = next((t for t in result.tasks if t.category == "examination"), None)
    assert exam_task is not None
    assert exam_task.event_date is not None or exam_task.needs_verification

    assign_task = next((t for t in result.tasks if t.category == "assignment"), None)
    assert assign_task is not None
    assert assign_task.deadline is not None or assign_task.needs_verification


def test_part3_specified_announcement_extraction():
    from backend.app.services.guardrail_service import guardrail_service
    prompt_text = (
        "Students must submit the DBMS Assignment 2 by November 15, 2026. "
        "The Machine Learning Lab Record must be completed by November 18, 2026. "
        "The Computer Networks internal examination will take place on November 20, 2026. "
        "The Mini Project Review is scheduled for November 22, 2026."
    )
    result = gemini_service.extract_tasks_from_text(prompt_text)
    guarded = guardrail_service.validate_and_filter_tasks(result)
    
    assert len(guarded.tasks) == 4
    categories = [t.category for t in guarded.tasks]
    assert "assignment" in categories
    assert "lab" in categories
    assert "examination" in categories
    assert "project" in categories

    # Check date formats and separation
    dbms_task = next(t for t in guarded.tasks if "DBMS" in t.title or t.subject == "DBMS")
    assert dbms_task.deadline == "2026-11-15"
    assert dbms_task.event_date is None

    exam_task = next(t for t in guarded.tasks if t.category == "examination")
    assert exam_task.event_date == "2026-11-20"
    assert exam_task.deadline is None

def test_gemini_model_configuration_and_diagnostics():
    from backend.app.core.config import settings
    assert settings.GEMINI_MODEL == "gemini-3.5-flash-lite"
    assert gemini_service.model_name == "gemini-3.5-flash-lite"

    diagnostics = gemini_service.test_connection()
    assert isinstance(diagnostics, dict)
    assert diagnostics["model"] == "gemini-3.5-flash-lite"
    assert diagnostics["sdk"] == "google-genai"
    assert "configured" in diagnostics
    assert "connected" in diagnostics

def test_extracted_task_supporting_evidence_and_mode():
    text = "AI project synopsis submission is due on November 25, 2026. Submit through the classroom portal."
    result = gemini_service.extract_tasks_from_text(text)
    assert result.model_used == "gemini-3.5-flash-lite"
    assert result.extraction_mode in ["live_gemini", "deterministic_fallback"]
    assert len(result.tasks) >= 1
    task = result.tasks[0]
    assert task.supporting_evidence is not None
