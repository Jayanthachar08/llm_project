from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, date

class ExtractedTaskItem(BaseModel):
    title: str = Field(..., description="Clear, concise task title")
    subject: Optional[str] = Field(None, description="Identified academic subject or course code")
    category: str = Field("assignment", description="assignment, examination, event, lab, project")
    description: Optional[str] = Field(None, description="Detailed description or context")
    deadline: Optional[str] = Field(None, description="Submission deadline in YYYY-MM-DD or YYYY-MM-DDTHH:MM format. Must be null if no explicit deadline.")
    event_date: Optional[str] = Field(None, description="Examination date or academic event date in YYYY-MM-DD or YYYY-MM-DDTHH:MM format.")
    instructions: List[str] = Field(default_factory=list, description="Specific instructions, modules, or rules extracted from text")
    estimated_duration: Optional[float] = Field(2.0, description="Estimated hours required to prepare/complete")
    difficulty: Optional[str] = Field("Medium", description="Easy, Medium, Difficult")
    importance: Optional[str] = Field("Normal", description="Normal, Important, Critical")
    needs_verification: bool = Field(False, description="True if dates/details are ambiguous or incomplete")
    verification_reason: Optional[str] = Field(None, description="Explanation why student verification is required")
    supporting_evidence: Optional[str] = Field(None, description="Direct text snippet from announcement or source supporting this task")
    source_document: Optional[str] = Field(None, description="Source document name if retrieved from RAG")
    source_page: Optional[int] = Field(None, description="Page number of source document if retrieved from RAG")

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if any(k in v_clean for k in ["exam", "test", "midterm", "internal", "final", "viva", "assessment"]):
            return "examination"
        if "quiz" in v_clean:
            return "quiz"
        if any(k in v_clean for k in ["presentation", "seminar"]):
            return "presentation"
        if "report" in v_clean:
            return "report"
        if "lab" in v_clean or "practical" in v_clean:
            return "lab"
        if "proj" in v_clean:
            return "project"
        if any(k in v_clean for k in ["event", "workshop", "symposium", "hackathon"]):
            return "event"
        return "assignment"

    @field_validator("difficulty")
    @classmethod
    def normalize_difficulty(cls, v: Optional[str]) -> str:
        if not v:
            return "Medium"
        v_clean = v.strip().capitalize()
        return v_clean if v_clean in ["Easy", "Medium", "Difficult"] else "Medium"

    @field_validator("importance")
    @classmethod
    def normalize_importance(cls, v: Optional[str]) -> str:
        if not v:
            return "Normal"
        v_clean = v.strip().capitalize()
        return v_clean if v_clean in ["Normal", "Important", "Critical"] else "Normal"

class GeminiExtractionResult(BaseModel):
    tasks: List[ExtractedTaskItem] = Field(default_factory=list)
    raw_summary: Optional[str] = Field(None, description="Short summary of announcement")
    ambiguity_detected: bool = Field(False)
    model_used: Optional[str] = Field("gemini-3.5-flash-lite", description="LLM model identifier used for extraction")
    extraction_mode: Optional[str] = Field("deterministic_fallback", description="live_gemini or deterministic_fallback")
