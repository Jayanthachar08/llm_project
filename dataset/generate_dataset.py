import json
import os

def generate_caad_dataset():
    announcements = []
    
    # 1. 30 Assignment announcements
    assignment_templates = [
        ("DBMS", "Database Management Systems", "Assignment {num}: Write SQL queries for relational schema and normalize up to BCNF. Submit hardcopy and PDF report before November {day}, 2026.", 10),
        ("CN", "Computer Networks", "CN Assignment {num}: Implement socket programming in Python (TCP and UDP client-server). Submission deadline is November {day}, 2026 at 5:00 PM.", 10),
        ("AI", "Artificial Intelligence", "AI Problem Set {num}: Solve A* search and Alpha-Beta pruning algorithms. Submit your typed report by November {day}, 2026.", 10)
    ]
    
    ann_id = 1
    for subj_code, subj_name, template, count in assignment_templates:
        for i in range(1, count + 1):
            day = 10 + i
            text = template.format(num=i, day=day)
            announcements.append({
                "announcement_id": f"CAAD_ASSIGN_{ann_id:03d}",
                "announcement_text": text,
                "source_type": "text",
                "expected_tasks": [f"{subj_code} Assignment {i}" if "Assignment" in text else f"{subj_code} Problem Set {i}"],
                "expected_subjects": [subj_code],
                "expected_categories": ["assignment"],
                "expected_deadlines": [f"November {day}, 2026"],
                "expected_event_dates": [None],
                "expected_instructions": ["Submit before deadline"],
                "ambiguity_status": False
            })
            ann_id += 1

    # 2. 20 Examination announcements
    exam_templates = [
        ("DBMS", "First Internal Assessment for DBMS will be held on November {day}, 2026 from 10:00 AM to 11:30 AM. Syllabus covers Modules 1 and 2.", 10),
        ("Operating Systems", "Mid-term Examination for Operating Systems is scheduled on November {day}, 2026. Prepare CPU scheduling, deadlocks, and virtual memory.", 10)
    ]
    exam_id = 1
    for subj, template, count in exam_templates:
        for i in range(1, count + 1):
            day = 15 + i
            text = template.format(day=day)
            announcements.append({
                "announcement_id": f"CAAD_EXAM_{exam_id:03d}",
                "announcement_text": text,
                "source_type": "text",
                "expected_tasks": [f"{subj} Internal Assessment" if "Internal" in text else f"{subj} Mid-term Examination"],
                "expected_subjects": [subj],
                "expected_categories": ["examination"],
                "expected_deadlines": [None],
                "expected_event_dates": [f"November {day}, 2026"],
                "expected_instructions": ["Prepare modules"],
                "ambiguity_status": False
            })
            exam_id += 1

    # 3. 15 Laboratory announcements
    lab_id = 1
    for i in range(1, 16):
        day = 10 + (i % 15) + 1
        text = f"DBMS Laboratory Experiment {i}: Execute triggers and stored procedures. Complete the observation record and get it evaluated on November {day}, 2026."
        announcements.append({
            "announcement_id": f"CAAD_LAB_{lab_id:03d}",
            "announcement_text": text,
            "source_type": "text",
            "expected_tasks": [f"DBMS Lab Experiment {i}"],
            "expected_subjects": ["DBMS"],
            "expected_categories": ["lab"],
            "expected_deadlines": [f"November {day}, 2026"],
            "expected_event_dates": [None],
            "expected_instructions": ["Execute triggers and stored procedures"],
            "ambiguity_status": False
        })
        lab_id += 1

    # 4. 15 Academic Event announcements
    event_id = 1
    events = [
        "Annual College Technical Symposium 'TechFest 2026'",
        "Guest Lecture on Deep Learning and Generative AI",
        "National Level Hackathon 2026",
        "Workshop on Cloud Computing with AWS and Docker",
        "Department Orientation Program for Final Year Students"
    ]
    for i in range(1, 16):
        evt = events[(i - 1) % len(events)]
        day = 12 + i
        text = f"{evt} will take place on November {day}, 2026 at the Main Auditorium starting at 9:30 AM. Attendance is mandatory."
        announcements.append({
            "announcement_id": f"CAAD_EVENT_{event_id:03d}",
            "announcement_text": text,
            "source_type": "text",
            "expected_tasks": [evt],
            "expected_subjects": ["General"],
            "expected_categories": ["event"],
            "expected_deadlines": [None],
            "expected_event_dates": [f"November {day}, 2026"],
            "expected_instructions": ["Attendance is mandatory"],
            "ambiguity_status": False
        })
        event_id += 1

    # 5. 10 Ambiguous announcements (missing calendar context or relative dates)
    ambig_id = 1
    ambig_texts = [
        "Students are requested to submit the DBMS assignment next Monday without fail.",
        "Kindly submit your project synopsis as soon as possible to the department office.",
        "The internal test will be conducted tomorrow afternoon in Room 302.",
        "Submit the CN lab manual before next week or marks will be deducted.",
        "Complete the course survey by end of week.",
        "The seminar presentation will be held coming Wednesday.",
        "Students must upload their internship certificates shortly.",
        "Submit remaining assignment problems soon.",
        "Internal test marks verification tomorrow at 2 PM.",
        "Lab records must be signed by next Friday."
    ]
    for text in ambig_texts:
        announcements.append({
            "announcement_id": f"CAAD_AMBIG_{ambig_id:03d}",
            "announcement_text": text,
            "source_type": "text",
            "expected_tasks": ["Academic Activity"],
            "expected_subjects": ["General"],
            "expected_categories": ["assignment"],
            "expected_deadlines": [None],
            "expected_event_dates": [None],
            "expected_instructions": ["Student verification required"],
            "ambiguity_status": True
        })
        ambig_id += 1

    # 6. 10 Multiple-task announcements
    multi_id = 1
    multi_texts = [
        "Students must complete the DBMS assignment before November 18, 2026. The CN assignment is due on November 20, 2026. Also, the DBMS internal test is scheduled on November 22, 2026.",
        "Submit the AI lab record by November 15, 2026. Prepare for the Machine Learning quiz on November 17, 2026. Project abstract submission is due November 25, 2026.",
        "Operating Systems assignment is due on November 14, 2026. The OS lab viva will be conducted on November 19, 2026.",
        "Submit the Cloud Computing assignment on November 16, 2026 and attend the AWS certification workshop on November 21, 2026.",
        "Final Year Project Phase 1 report due on November 24, 2026. Project presentation will be held on November 28, 2026.",
        "Python mini-project code submission by November 15, 2026. Demonstration and viva on November 18, 2026.",
        "Software Engineering UML diagrams assignment due on November 12, 2026. Internal exam scheduled on November 26, 2026.",
        "Computer Networks lab submission on November 16, 2026. CN theory test on November 23, 2026.",
        "Submit AI research paper summary on November 19, 2026. The robotics seminar will take place on November 27, 2026.",
        "DBMS indexing assignment is due on November 17, 2026. Final lab exam will be held on November 29, 2026."
    ]
    for text in multi_texts:
        announcements.append({
            "announcement_id": f"CAAD_MULTI_{multi_id:03d}",
            "announcement_text": text,
            "source_type": "text",
            "expected_tasks": ["Multiple Tasks"],
            "expected_subjects": ["DBMS", "CN", "AI", "OS"],
            "expected_categories": ["assignment", "examination"],
            "expected_deadlines": ["Varies"],
            "expected_event_dates": ["Varies"],
            "expected_instructions": ["Complete all activities"],
            "ambiguity_status": False
        })
        multi_id += 1

    os.makedirs("./dataset", exist_ok=True)
    with open("./dataset/announcements.json", "w", encoding="utf-8") as f:
        json.dump(announcements, f, indent=2)

    print(f"Generated CAAD dataset with {len(announcements)} records successfully.")

if __name__ == "__main__":
    generate_caad_dataset()
