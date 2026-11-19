# CampusFlow AI – Database Design

## Database Schema (PostgreSQL & SQLAlchemy)

CampusFlow AI utilizes 11 relational entities configured with foreign keys and cascading rules.

### 1. `users`
- `id` (PK, Integer, autoincrement)
- `name` (String 100, not null)
- `email` (String 255, unique, not null, index)
- `password_hash` (String 255, bcrypt, not null)
- `created_at` (DateTime with timezone)

### 2. `subjects`
- `id` (PK, Integer)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `subject_name` (String 100, not null)
- `subject_code` (String 20, nullable)
- `created_at` (DateTime with timezone)

### 3. `announcements`
- `id` (PK, Integer)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `file_name` (String 255, nullable)
- `file_type` (String 50, nullable)
- `extracted_text` (Text, not null)
- `source_type` (String 50: pdf, image, text)
- `processing_status` (String 50: pending, processed, error)
- `created_at` (DateTime with timezone)

### 4. `document_chunks` (RAG Vector Store Reference)
- `id` (PK, Integer)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `announcement_id` (FK -> announcements.id, ondelete=CASCADE)
- `document_name` (String 255)
- `page_number` (Integer, default 1)
- `chunk_index` (Integer, default 0)
- `content` (Text, not null)
- `source_type` (String 50)
- `created_at` (DateTime with timezone)

### 5. `tasks`
- `id` (PK, Integer)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `announcement_id` (FK -> announcements.id, ondelete=SET NULL, nullable)
- `subject_id` (FK -> subjects.id, ondelete=SET NULL, nullable)
- `title` (String 255, not null)
- `description` (Text, nullable)
- `category` (String 50: assignment, examination, lab, project, event)
- `deadline` (DateTime with timezone, nullable)
- `event_date` (DateTime with timezone, nullable)
- `importance` (String 50: Normal, Important, Critical)
- `difficulty` (String 50: Easy, Medium, Difficult)
- `estimated_duration` (Float, hours)
- `priority_score` (Float, 0 to 100)
- `status` (String 50: Not Started, In Progress, Completed)
- `confirmation_status` (String 50: pending, confirmed, rejected)
- `created_at`, `updated_at` (DateTime with timezone)

### 6. `student_availability`
- `id` (PK, Integer)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `day_of_week` (String 20: Monday to Sunday)
- `start_time` (String 10: HH:MM, e.g. "18:00")
- `end_time` (String 10: HH:MM, e.g. "22:00")
- `is_available` (Boolean, default True)

### 7. `college_schedules`
- `id` (PK, Integer)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `title` (String 100)
- `day_of_week` (String 20, nullable)
- `start_time` (String 10: HH:MM, e.g. "09:00")
- `end_time` (String 10: HH:MM, e.g. "16:00")
- `event_date` (Date, nullable)
- `schedule_type` (String 50: college_hours, class, lab, exam)

### 8. `study_sessions`
- `id` (PK, Integer)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `task_id` (FK -> tasks.id, ondelete=CASCADE)
- `session_date` (Date, not null, index)
- `start_time` (String 10: HH:MM)
- `end_time` (String 10: HH:MM)
- `duration` (Float, minutes)
- `status` (String 50: scheduled, completed, missed, cancelled)
- `created_at` (DateTime with timezone)

### 9. `task_progress`
- `id` (PK, Integer)
- `task_id` (FK -> tasks.id, ondelete=CASCADE)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `progress_percentage` (Float, 0 to 100)
- `status` (String 50)
- `notes` (Text, nullable)
- `updated_at` (DateTime with timezone)

### 10. `notifications`
- `id` (PK, Integer)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `task_id` (FK -> tasks.id, ondelete=CASCADE, nullable)
- `notification_type` (String 50: deadline, session, conflict, overdue)
- `message` (Text)
- `scheduled_at` (DateTime with timezone)
- `sent_at` (DateTime with timezone, nullable)
- `status` (String 50: pending, sent, read)

### 11. `schedule_change_history`
- `id` (PK, Integer)
- `user_id` (FK -> users.id, ondelete=CASCADE)
- `task_id` (FK -> tasks.id, ondelete=SET NULL, nullable)
- `change_type` (String 50: reschedule, delay, completion, manual_edit)
- `reason` (Text)
- `previous_state` (Text, nullable)
- `new_state` (Text, nullable)
- `created_at` (DateTime with timezone)
