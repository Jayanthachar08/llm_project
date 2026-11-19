import pytest
from datetime import datetime, timezone
from backend.app.models.user import User
from backend.app.models.announcement import Announcement
from backend.app.models.task import Task
from backend.app.models.subject import Subject

def test_progress_and_availability_routes(client, db_session):
    # Register test student
    reg = client.post("/api/auth/register", json={
        "name": "Route Tester",
        "email": "routes@campusflow.edu",
        "password": "Password123!"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    user_id = reg.json()["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test availability endpoints
    avail_payload = {
        "availabilities": [
            {"day_of_week": "Monday", "start_time": "18:00", "end_time": "21:00", "is_available": True},
            {"day_of_week": "Tuesday", "start_time": "18:00", "end_time": "21:00", "is_available": True}
        ]
    }
    put_res = client.put("/api/availability", json=avail_payload, headers=headers)
    assert put_res.status_code == 200
    assert len(put_res.json()) == 2

    get_res = client.get("/api/availability", headers=headers)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 2

    # 2. Add sample task and subject for progress routes
    subj = Subject(user_id=user_id, subject_name="Operating Systems", subject_code="CS701")
    db_session.add(subj)
    db_session.commit()
    db_session.refresh(subj)

    task = Task(
        user_id=user_id,
        subject_id=subj.id,
        title="OS Kernel Scheduling",
        category="assignment",
        deadline=datetime(2026, 11, 20, 18, 0, tzinfo=timezone.utc),
        status="Not Started",
        confirmation_status="confirmed",
        estimated_duration=3.0,
        priority_score=75.0
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    # 3. Test progress summary
    prog_res = client.get("/api/progress/summary", headers=headers)
    assert prog_res.status_code == 200
    data = prog_res.json()
    assert data["total_tasks"] >= 1
    assert "completion_percentage" in data

    # 4. Test subject progress
    subj_res = client.get("/api/progress/subjects", headers=headers)
    assert subj_res.status_code == 200
    subjects = subj_res.json()
    assert any(s["subject_name"] == "Operating Systems" for s in subjects)

    # 5. Test complete task
    complete_res = client.patch(f"/api/tasks/{task.id}/complete", headers=headers)
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "Completed"

    # 6. Test announcement extract by ID
    ann = Announcement(
        user_id=user_id,
        file_name="lab_notice.txt",
        file_type="text/plain",
        extracted_text="Operating Systems Lab assignment due on 2026-11-25.",
        source_type="text",
        processing_status="processed"
    )
    db_session.add(ann)
    db_session.commit()
    db_session.refresh(ann)

    extract_res = client.post(f"/api/announcements/{ann.id}/extract", headers=headers)
    assert extract_res.status_code == 200
    extract_data = extract_res.json()
    assert "tasks" in extract_data
