import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.database.connection import init_db
from backend.app.scheduler.reminders import start_scheduler, shutdown_scheduler
from backend.app.routers.auth import router as auth_router
from backend.app.routers.profile import router as profile_router
from backend.app.routers.announcements import router as announcements_router
from backend.app.routers.rag import router as rag_router
from backend.app.routers.tasks import router as tasks_router
from backend.app.routers.planner import router as planner_router
from backend.app.routers.notifications import router as notifications_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.progress import router as progress_router
from backend.app.routers.availability import router as availability_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    init_db()
    try:
        start_scheduler()
    except Exception as e:
        print(f"Notice: APScheduler could not start: {e}")
    yield
    # Shutdown actions
    try:
        shutdown_scheduler()
    except Exception:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(profile_router, prefix=settings.API_V1_PREFIX)
app.include_router(announcements_router, prefix=settings.API_V1_PREFIX)
app.include_router(rag_router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks_router, prefix=settings.API_V1_PREFIX)
app.include_router(planner_router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(progress_router, prefix=settings.API_V1_PREFIX)
app.include_router(availability_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "status": "online",
        "docs": "/docs"
    }

@app.get("/api/health")
def health_check():
    from backend.app.services.gemini_service import gemini_service
    llm_status = gemini_service.test_connection()
    return {
        "status": "healthy",
        "service": "CampusFlow AI Backend API",
        "version": "1.0.0",
        "llm": {
            "model_configured": settings.GEMINI_MODEL,
            "connected": llm_status.get("connected", False),
            "status": "online" if llm_status.get("connected") else "offline_fallback_active",
            "diagnostics": llm_status
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
