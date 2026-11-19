import pytest
from backend.app.services.rag_service import rag_service
from backend.app.services.gemini_service import gemini_service
from backend.app.services.guardrail_service import guardrail_service

def test_rag_two_document_grounding_demonstration(db_session):
    user_a_id = 101
    user_b_id = 102

    # DOCUMENT 1: Academic calendar containing examination dates
    doc1_name = "College_Academic_Calendar_2026.pdf"
    doc1_text = (
        "NATIONAL INSTITUTE OF ENGINEERING - ACADEMIC CALENDAR 2026\n"
        "Page 1: 7th Semester Examination Schedules\n"
        "Course CS701 Database Management Systems Final Theory Examination is scheduled on December 05, 2026 from 9:30 AM to 12:30 PM.\n"
        "Students must report to Examination Hall A with identity cards."
    )
    chunks_doc1 = rag_service.ingest_document(
        user_id=user_a_id,
        document_id=1,
        document_name=doc1_name,
        text=doc1_text,
        source_type="pdf",
        db=db_session
    )
    assert chunks_doc1 >= 1

    # DOCUMENT 2: Assignment announcement containing submission deadline
    doc2_name = "DBMS_Assignment_Circular.pdf"
    doc2_text = (
        "DEPARTMENT OF COMPUTER SCIENCE\n"
        "Course CS701 Database Management Systems\n"
        "Assignment 3 and Hospital Case Study Deliverables must be submitted before November 28, 2026 at 5:00 PM.\n"
        "Late submissions will carry a 20% penalty."
    )
    chunks_doc2 = rag_service.ingest_document(
        user_id=user_a_id,
        document_id=2,
        document_name=doc2_name,
        text=doc2_text,
        source_type="pdf",
        db=db_session
    )
    assert chunks_doc2 >= 1

    # QUERY: A new brief announcement referring to the assignment and examination
    query_text = (
        "Attention 7th semester students: CS701 course wrap-up. "
        "Please submit your CS701 assignment deliverables as scheduled earlier and prepare for the CS701 theory examination."
    )

    # 1. Perform RAG Semantic Retrieval
    retrieved_chunks = rag_service.search_similar_context(
        user_id=user_a_id,
        query=query_text,
        top_k=4
    )
    assert len(retrieved_chunks) >= 2

    # Check source attribution (document name and page number)
    doc_names = [c["document_name"] for c in retrieved_chunks]
    assert doc1_name in doc_names
    assert doc2_name in doc_names
    for c in retrieved_chunks:
        assert "page_number" in c
        assert c["page_number"] >= 1
        assert "content" in c

    # 2. Build Augmented Context for Gemini
    context_str = "\n".join([
        f"[Source: {c['document_name']}, Page {c['page_number']}]: {c['content']}"
        for c in retrieved_chunks
    ])
    assert "College_Academic_Calendar_2026.pdf" in context_str
    assert "DBMS_Assignment_Circular.pdf" in context_str

    # 3. Grounded Extraction with RAG Context
    res = gemini_service.extract_tasks_from_text(query_text, rag_context=context_str)
    guarded = guardrail_service.validate_and_filter_tasks(res)
    assert len(guarded.tasks) >= 2

    # Check that categories and dates are correctly grounded from retrieved documents
    categories = [t.category for t in guarded.tasks]
    assert "assignment" in categories
    assert "examination" in categories

    # 4. Cross-User Isolation Verification
    # User B searching the same query should retrieve NOTHING from User A
    user_b_chunks = rag_service.search_similar_context(
        user_id=user_b_id,
        query=query_text,
        top_k=4
    )
    assert len(user_b_chunks) == 0

    # 5. Document Deletion & Re-indexing
    rag_service.delete_document(user_id=user_a_id, document_id=1, db=db_session)
    remaining_chunks = rag_service.search_similar_context(
        user_id=user_a_id,
        query="examination schedule",
        top_k=2
    )
    # Doc 1 should be gone
    assert not any(c["document_name"] == doc1_name for c in remaining_chunks)
