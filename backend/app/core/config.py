import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "CampusFlow AI: An LLM-Powered Academic Task Planning and Deadline Management System"
    PROJECT_DESCRIPTION: str = (
        "CampusFlow AI is an LLM-powered system that converts academic announcements, assignments, "
        "and schedules into organized tasks. It identifies deadlines, prioritizes tasks, detects scheduling "
        "conflicts, and generates personalized study plans. It also provides reminders, progress tracking, "
        "and dynamic schedule updates, helping students manage responsibilities and avoid missed deadlines."
    )
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/campusflow_db"
    USE_SQLITE_FALLBACK: bool = True
    
    # Security
    JWT_SECRET: str = "campusflow_super_secret_jwt_key_academic_task_planner_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Gemini LLM
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    
    # Storage & OCR
    UPLOAD_DIR: str = "./uploads"
    TESSERACT_CMD: str = ""
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
