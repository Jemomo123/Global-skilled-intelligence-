import logging
from sqlmodel import SQLModel, create_engine, Session, Field
from app.config import settings

logger = logging.getLogger("DatabaseEngine")

# Master Production Job Model definition shared across API and Scanner loops
class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    company: str
    location: str = ""
    country: str = ""
    job_url: str = "#"
    visa_sponsored: bool = False
    work_permit: bool = False
    relocation: bool = False
    cv_match: bool = False
    cv_match_pct: int = 0

# Configuration matching your Render Postgres or SQLite engine pool
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

def init_db():
    """
    Priority 7 & 8: Production readiness data model alignment. 
    Forces table recreation to ensure new columns exist.
    """
    try:
        logger.info("⚙️ Initializing database structure verification...")
        # Force drop to clean old structural versions causing silent write rollbacks
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
        logger.info("✅ Database tables successfully built with latest engine schema.")
    except Exception as e:
        logger.critical(f"❌ Database initialization sequence failed: {e}")
        raise e

def get_db():
    """
    Context manager yield loop providing isolated transaction sessions.
    """
    with Session(engine) as session:
        yield session
