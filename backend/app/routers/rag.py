from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.announcement import Announcement
from backend.app.services.rag_service import rag_service
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/rag", tags=["Retrieval-Augmented Generation (RAG)"])

class RAGIngestRequest(BaseModel):
    document_id: Optional[int] = None
    document_name: str = Field(..., min_length=1)
    text: str = Field(..., min_length=10)
    source_type: str = "pdf"

class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = 3

class RAGSearchResultItem(BaseModel):
    content: str
    document_name: str
    document_id: Optional[int] = None
    page_number: int
    source_type: str
    distance: float

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_document_for_rag(
    payload: RAGIngestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    RAG Pipeline: Chunk, embed, and store document in persistent ChromaDB
    with strict user-level metadata isolation.
    """
    doc_id = payload.document_id or 0
    chunks_created = rag_service.ingest_document(
        user_id=current_user.id,
        document_id=doc_id,
        document_name=payload.document_name,
        text=payload.text,
        source_type=payload.source_type,
        db=db
    )
    return {
        "message": f"Successfully ingested {chunks_created} vector chunks into knowledge base.",
        "document_name": payload.document_name,
        "chunks_indexed": chunks_created
    }

@router.post("/search", response_model=List[RAGSearchResultItem])
def search_knowledge_base(
    payload: RAGSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Semantic Document Retrieval:
    Retrieves most relevant document chunks for the authenticated student
    with source attribution (document name, page number).
    """
    results = rag_service.search_similar_context(
        user_id=current_user.id,
        query=payload.query,
        top_k=payload.top_k
    )
    return [
        RAGSearchResultItem(
            content=r["content"],
            document_name=r["document_name"],
            document_id=int(r["document_id"]) if r.get("document_id") and str(r["document_id"]).isdigit() else None,
            page_number=r["page_number"],
            source_type=r["source_type"],
            distance=r["distance"]
        ) for r in results
    ]

@router.delete("/documents/{document_id}", status_code=status.HTTP_200_OK)
def delete_rag_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document chunks from both ChromaDB vector store and relational database."""
    rag_service.delete_document(current_user.id, document_id, db=db)
    return {"message": f"Document #{document_id} successfully removed from RAG index."}

@router.post("/reindex", status_code=status.HTTP_200_OK)
def reindex_user_knowledge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rebuild all ChromaDB vector embeddings for the student from persistent database records."""
    total = rag_service.reindex_all_for_user(current_user.id, db)
    return {"message": f"Re-indexed {total} chunks in vector collection."}
