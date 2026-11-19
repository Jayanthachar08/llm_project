from backend.app.schemas.user import UserRegister, UserLogin, UserResponse, Token
from backend.app.schemas.subject import SubjectCreate, SubjectResponse
from backend.app.schemas.announcement import AnnouncementCreate, AnnouncementResponse
from backend.app.schemas.gemini import ExtractedTaskItem, GeminiExtractionResult
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskConfirmItem, TaskConfirmBatch, TaskPriorityDetail
from backend.app.schemas.availability import AvailabilityCreate, AvailabilityResponse, AvailabilityBatchUpdate
from backend.app.schemas.college_schedule import CollegeScheduleCreate, CollegeScheduleResponse, CollegeScheduleBatchUpdate
from backend.app.schemas.study_session import StudySessionCreate, StudySessionUpdate, StudySessionResponse
from backend.app.schemas.task_progress import TaskProgressCreate, TaskProgressUpdate, TaskProgressResponse
from backend.app.schemas.notification import NotificationResponse
from backend.app.schemas.dashboard import DashboardSummary, ConflictItem, SubjectProgressItem

__all__ = [
    "UserRegister", "UserLogin", "UserResponse", "Token",
    "SubjectCreate", "SubjectResponse",
    "AnnouncementCreate", "AnnouncementResponse",
    "ExtractedTaskItem", "GeminiExtractionResult",
    "TaskCreate", "TaskUpdate", "TaskResponse", "TaskConfirmItem", "TaskConfirmBatch", "TaskPriorityDetail",
    "AvailabilityCreate", "AvailabilityResponse", "AvailabilityBatchUpdate",
    "CollegeScheduleCreate", "CollegeScheduleResponse", "CollegeScheduleBatchUpdate",
    "StudySessionCreate", "StudySessionUpdate", "StudySessionResponse",
    "TaskProgressCreate", "TaskProgressUpdate", "TaskProgressResponse",
    "NotificationResponse",
    "DashboardSummary", "ConflictItem", "SubjectProgressItem"
]
