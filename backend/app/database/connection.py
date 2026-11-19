import logging
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from backend.app.core.config import settings
from backend.app.database.base import Base

logger = logging.getLogger("campusflow.database")
logging.basicConfig(level=logging.INFO)

def create_app_engine():
    """Create SQLAlchemy engine with fallback support."""
    database_url = settings.DATABASE_URL
    try:
        # Attempt connecting to configured primary database (PostgreSQL)
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3} if "postgres" in database_url else {}
        )
        with engine.connect() as conn:
            logger.info("Successfully connected to primary database: %s", database_url.split("@")[-1] if "@" in database_url else database_url)
        return engine
    except Exception as e:
        if settings.USE_SQLITE_FALLBACK:
            fallback_url = "sqlite:///./campusflow.db"
            logger.warning(
                "Primary database (%s) unavailable (%s). Falling back to SQLite: %s",
                database_url, str(e), fallback_url
            )
            fallback_engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False}
            )
            
            # Enable SQLite foreign key enforcement
            @event.listens_for(fallback_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
                
            return fallback_engine
        else:
            logger.error("Failed to connect to database and fallback is disabled.")
            raise e

engine = create_app_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all registered database tables."""
    # Import all models before create_all
    import backend.app.models
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
