import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.connection import init_db

def run_e2e_verification():
    init_db()
    client = TestClient(app)
    
    # 1. Open CampusFlow AI & Health Check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    
    # 2. Register a student
    test_email = f"student_{int(datetime.now().timestamp())}@university.edu"
    test_password = "SecurePassword123!"
    reg_data = {
        "email": test_email,
        "name": "Arjun Sharma",
        "password": test_password
    }
    res = client.post("/api/auth/register", json=reg_data)
    assert res.status_code == 201, f"Registration failed: {res.text}"
    auth_data = res.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Log in (verify authentication flow)
    login_res = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert login_res.status_code == 200

    # 4. Update student profile
    prof_update = client.put("/api/profile", json={"name": "Arjun Sharma (Final Year CSE)"}, headers=headers)
    assert prof_update.status_code == 200
    assert prof_update.json()["name"] == "Arjun Sharma (Final Year CSE)"

    # 5. Add academic subjects
    subj_res1 = client.post("/api/profile/subjects", json={"subject_name": "Database Management Systems", "subject_code": "CS701"}, headers=headers)
    assert subj_res1.status_code == 201
    subj_res2 = client.post("/api/profile/subjects", json={"subject_name": "Artificial Intelligence", "subject_code": "CS702"}, headers=headers)
    assert subj_res2.status_code == 201

    # 6. Enter college timetable
    college_sched = {
        "schedules": [
            {"title": "Morning Lectures", "day_of_week": day, "start_time": "09:00", "end_time": "16:00", "schedule_type": "college_hours"}
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        ]
    }
    col_res = client.put("/api/profile/college-schedule", json=college_sched, headers=headers)
    assert col_res.status_code == 200

    # 7. Enter study availability
    avail_data = {
        "availabilities": [
            {"day_of_week": day, "start_time": "18:00", "end_time": "22:00", "is_available": True}
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        ]
    }
    avail_res = client.put("/api/availability", json=avail_data, headers=headers)
    assert avail_res.status_code == 200

    # 8. Upload an academic announcement (Text Paste)
    future_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    exam_date = (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d")
    announcement_text = f"""
    DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING
    CIRCULAR: 7th SEMESTER IMPORTANT DEADLINES
    
    1. Database Management Systems (DBMS) - Assignment 2:
       Design an E-R diagram and normalize up to BCNF for the hospital management case study.
       Hard deadline for submission is {future_date} at 5:00 PM. No late submissions will be entertained.
       
    2. Artificial Intelligence (AI) - Mid-Term Theory Examination:
       The second internal assessment test will be conducted on {exam_date} from 10:00 AM to 12:00 PM.
       Portion includes Modules 1, 2, and 3 (Search algorithms and Knowledge representation).
    """
    res = client.post("/api/announcements/paste-text", json={
        "text": announcement_text
    }, headers=headers)
    assert res.status_code == 201
    announcement_id = res.json()["id"]

    # 9. Extract document text & 10. RAG Ingest and Knowledge Retrieval
    rag_payload = {
        "document_id": announcement_id,
        "document_name": "CSE_Circular_Nov_2026.txt",
        "text": announcement_text,
        "source_type": "text"
    }
    rag_ingest_res = client.post("/api/rag/ingest", json=rag_payload, headers=headers)
    assert rag_ingest_res.status_code == 201
    
    rag_query_res = client.post("/api/rag/search", json={
        "query": "What are the portions for the AI internal test?",
        "top_k": 2
    }, headers=headers)
    assert rag_query_res.status_code == 200

    # 11 & 12. Send announcement + RAG context to Gemini & extract structured activities
    extract_res = client.post("/api/announcements/extract", json={
        "text": announcement_text,
        "announcement_id": announcement_id,
        "use_rag": True
    }, headers=headers)
    assert extract_res.status_code == 200
    extracted_tasks = extract_res.json()["tasks"]
    assert len(extracted_tasks) >= 2

    # 13 & 14 & 15. Validate outputs using Guardrails & Edit and Confirm tasks
    confirm_payload = {
        "announcement_id": announcement_id,
        "tasks": [
            {
                "title": t["title"],
                "subject_name": "Database Management Systems" if "DBMS" in t["title"] else "Artificial Intelligence",
                "category": t["category"],
                "deadline": t.get("deadline"),
                "event_date": t.get("event_date"),
                "estimated_duration": t.get("estimated_duration") or 3.0,
                "difficulty": t.get("difficulty") or "Medium",
                "importance": t.get("importance") or "Important",
                "description": t.get("description") or ""
            }
            for t in extracted_tasks
        ]
    }
    
    # 16. Store tasks in database
    confirm_res = client.post("/api/tasks/confirm", json=confirm_payload, headers=headers)
    assert confirm_res.status_code == 201
    saved_tasks = confirm_res.json()
    assert len(saved_tasks) >= 2

    # 17. Calculate task priorities
    priorities_res = client.get("/api/tasks/priorities", headers=headers)
    assert priorities_res.status_code == 200
    assert len(priorities_res.json()) >= 2

    # 18. Detect scheduling conflicts
    conflicts_res = client.get("/api/planner/conflicts", headers=headers)
    assert conflicts_res.status_code == 200

    # 19. Generate a personalized study plan
    plan_res = client.post("/api/planner/generate", json={
        "session_duration": 60,
        "break_duration": 15,
        "horizon_days": 14,
        "preserve_completed": True
    }, headers=headers)
    assert plan_res.status_code == 200
    sessions = plan_res.json()["sessions"]
    assert len(sessions) >= 1

    # 20. Display the timetable on the calendar
    cal_res = client.get("/api/planner/calendar", headers=headers)
    assert cal_res.status_code == 200
    assert len(cal_res.json()) >= 1

    # 21. Generate deadline reminders
    notifs_res = client.get("/api/notifications", headers=headers)
    assert notifs_res.status_code == 200

    # 22. Update task progress & 23. Complete a task
    target_task_id = saved_tasks[0]["id"]
    complete_res = client.patch(f"/api/tasks/{target_task_id}/complete", headers=headers)
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "Completed"

    # 24. Miss a scheduled study session & 25. Perform dynamic rescheduling
    if len(sessions) > 1:
        missed_session_id = sessions[1]["id"]
        client.patch(f"/api/planner/sessions/{missed_session_id}", json={"status": "missed"}, headers=headers)
        resched_res = client.post("/api/planner/reschedule", json={"task_id": sessions[1]["task_id"]}, headers=headers)
        assert resched_res.status_code == 200

    # 26. Display updated dashboard statistics
    dash_res = client.get("/api/dashboard/summary", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["completed_tasks"] >= 1
    assert "completion_percentage" in dash_data

def test_e2e_full_workflow():
    run_e2e_verification()

if __name__ == "__main__":
    run_e2e_verification()
    print("All 26 E2E steps verified successfully!")
