# app/database.py
"""
Database Connection and Initialization.
"""

import logging
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

logger = logging.getLogger("Database")

# Single Unified Engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)


def create_db_and_tables():
    """Initializes database tables during application startup."""
    import app.models  # Ensures models are registered with SQLModel metadata
    logger.info("Initializing database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables verified/created successfully.")


def get_db():
    """FastAPI Dependency for database sessions."""
    with Session(engine) as session:
        yield session
