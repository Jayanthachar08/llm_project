import pytest
from backend.app.models.user import User
from backend.app.models.document_chunk import DocumentChunk
from backend.app.services.rag_service import rag_service

def test_rag_chunking():
    multipage_text = (
        "\n--- Page 1 ---\n"
        "Database Management Systems (DBMS) covers relational models, SQL queries, and normalization.\n"
        "\n--- Page 2 ---\n"
        "Computer Networks (CN) covers OSI model, TCP/IP protocol suite, and routing algorithms."
    )
    chunks = rag_service.chunk_text(multipage_text, chunk_size=200, overlap=20)
    assert len(chunks) >= 2
    pages = [c["page_number"] for c in chunks]
    assert 1 in pages
    assert 2 in pages

def test_rag_ingest_and_cross_user_isolation(db_session):
    # Setup 2 distinct users
    user1 = User(id=1, name="Alice", email="alice@test.edu", password_hash="hash")
    user2 = User(id=2, name="Bob", email="bob@test.edu", password_hash="hash")
    db_session.add_all([user1, user2])
    db_session.commit()

    # User 1 ingests DBMS syllabus
    rag_service.ingest_document(
        user_id=1,
        document_id=101,
        document_name="DBMS_Syllabus.pdf",
        text="All DBMS lab assignments must be implemented in PostgreSQL with normalization.",
        source_type="pdf",
        db=db_session
    )

    # User 2 ingests Computer Graphics syllabus
    rag_service.ingest_document(
        user_id=2,
        document_id=202,
        document_name="Graphics_Syllabus.pdf",
        text="Computer Graphics OpenGL shaders and rendering pipeline practicals.",
        source_type="pdf",
        db=db_session
    )

    # Verify User 1 search returns DBMS but NEVER User 2's documents
    user1_results = rag_service.search_similar_context(user_id=1, query="PostgreSQL lab assignments", top_k=3)
    assert len(user1_results) > 0
    assert user1_results[0]["document_name"] == "DBMS_Syllabus.pdf"
    for r in user1_results:
        assert "OpenGL" not in r["content"]

    # Verify User 2 search returns Graphics but NEVER User 1's documents
    user2_results = rag_service.search_similar_context(user_id=2, query="PostgreSQL lab assignments", top_k=3)
    # User 2 has NO DBMS documents, so User 2 should NOT retrieve User 1's DBMS document!
    for r in user2_results:
        assert r["document_name"] != "DBMS_Syllabus.pdf"
