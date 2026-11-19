from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.announcement import Announcement
from backend.app.schemas.announcement import AnnouncementResponse
from backend.app.schemas.gemini import GeminiExtractionResult
from backend.app.services.document_service import document_service
from backend.app.services.gemini_service import gemini_service
from backend.app.services.rag_service import rag_service
from backend.app.services.guardrail_service import guardrail_service
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/announcements", tags=["Announcements & Document Processing"])

class TextExtractRequest(BaseModel):
    text: str
    announcement_id: Optional[int] = None
    use_rag: bool = True

@router.post("/upload", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def upload_announcement_file(
    file: UploadFile = File(...),
    auto_rag_index: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an academic announcement document (PDF or image).
    Extracts text using PyMuPDF (text-based) or Pillow/Tesseract OCR (images/scanned).
    Automatically validates with Input Guardrails and optionally indexes into ChromaDB for RAG.
    """
    filename, source_type, extracted_text = await document_service.process_upload(file)
    
    # Layer 1 Input Guardrail
    sanitized_text = guardrail_service.validate_input_text(extracted_text)

    announcement = Announcement(
        user_id=current_user.id,
        file_name=filename,
        file_type=file.content_type or source_type,
        extracted_text=sanitized_text,
        source_type=source_type,
        processing_status="processed"
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    # Ingest into ChromaDB RAG Vector Store
    if auto_rag_index:
        try:
            rag_service.ingest_document(
                user_id=current_user.id,
                document_id=announcement.id,
                document_name=filename,
                text=sanitized_text,
                source_type=source_type,
                db=db
            )
        except Exception as e:
            # Non-blocking RAG index warning
            pass

    return announcement

@router.post("/paste-text", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def paste_announcement_text(
    payload: TextExtractRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Store raw pasted academic announcement text with Input Guardrails."""
    cleaned = document_service.process_pasted_text(payload.text)
    sanitized = guardrail_service.validate_input_text(cleaned)

    announcement = Announcement(
        user_id=current_user.id,
        file_name="pasted_text.txt",
        file_type="text/plain",
        extracted_text=sanitized,
        source_type="text",
        processing_status="processed"
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement

@router.post("/extract", response_model=GeminiExtractionResult)
def extract_tasks_with_gemini(
    payload: TextExtractRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete LLM Extraction Workflow:
    1. Input Guardrails validation & prompt injection neutralization.
    2. RAG Semantic Retrieval: fetches relevant syllabus/circular chunks from ChromaDB.
    3. Google GenAI LLM structured extraction with context augmentation.
    4. LLM Output Guardrails: date standardization, category verification, hallucination checks.
    5. Returns candidate tasks for Human-in-the-Loop review and confirmation.
    """
    text_to_process = payload.text
    if payload.announcement_id:
        ann = db.query(Announcement).filter(
            Announcement.id == payload.announcement_id,
            Announcement.user_id == current_user.id
        ).first()
        if ann:
            text_to_process = ann.extracted_text

    if not text_to_process or not text_to_process.strip():
        raise HTTPException(
            status_code=400,
            detail="No announcement text provided for Gemini extraction."
        )

    # 1. Input Guardrail
    sanitized_text = guardrail_service.validate_input_text(text_to_process)

    # 2. RAG Context Retrieval
    rag_context_str = ""
    if payload.use_rag:
        try:
            chunks = rag_service.search_similar_context(
                user_id=current_user.id,
                query=sanitized_text[:300],
                top_k=3
            )
            if chunks:
                rag_context_str = "\n".join([
                    f"[Source: {c['document_name']}, Page {c['page_number']}]: {c['content']}"
                    for c in chunks
                ])
        except Exception:
            pass

    # 3. GenAI Extraction with Prompt Engineering
    raw_result = gemini_service.extract_tasks_from_text(sanitized_text, rag_context=rag_context_str)

    # 4. Output Guardrail Filtering
    guarded_result = guardrail_service.validate_and_filter_tasks(raw_result)

    return guarded_result

@router.post("/{announcement_id}/extract", response_model=GeminiExtractionResult)
def extract_tasks_from_announcement_id(
    announcement_id: int,
    use_rag: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract tasks directly from a previously uploaded announcement ID."""
    ann = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.user_id == current_user.id
    ).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    payload = TextExtractRequest(
        text=ann.extracted_text,
        announcement_id=ann.id,
        use_rag=use_rag
    )
    return extract_tasks_with_gemini(payload=payload, current_user=current_user, db=db)

@router.get("", response_model=List[AnnouncementResponse])
def get_student_announcements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of uploaded announcements for authenticated student."""
    return db.query(Announcement).filter(
        Announcement.user_id == current_user.id
    ).order_by(Announcement.created_at.desc()).all()

@router.get("/{announcement_id}", response_model=AnnouncementResponse)
def get_announcement_by_id(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details of a single uploaded announcement."""
    ann = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.user_id == current_user.id
    ).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return ann
