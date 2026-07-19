import logging
import os
from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import SQLModel, Session, create_engine, select

from app.scheduler import start_scheduler
from app.api.health import router as health_router

# Setup unified application logging matrix
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GlobalApplicationMain")

app = FastAPI(
    title="Global Skilled Intelligence",
    description="Skilled trade intelligence & live discovery service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Repository Path Declarations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

try:
    if os.path.exists(STATIC_DIR):
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
except Exception as e:
    logger.warning(f"Static directory mounting skipped: {e}")

# Database Engine Fallback Connection Matrix
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jobs.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Register the production API routing interfaces
app.include_router(health_router)

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI Lifecycle: Initializing system startup routing...")
    start_scheduler()
    logger.info("FastAPI Lifecycle: Startup sequence fully completed.")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    Authoritative root endpoint rendering the dashboard interface.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/status")
def read_status():
    """
    Preserves the raw JSON metadata status string for health checks.
    """
    return {"status": "online", "framework": "Phase 2 Production Modular"}

# =====================================================================
# PRODUCTION API ROUTING LAYER (FRONTEND ↔ BACKEND LINK)
# =====================================================================

@app.get("/api/jobs")
def get_api_jobs(country: str = Query(None)):
    """
    Fetches raw jobs directly from SQLModel storage and formats them 
    into the metrics matrix and payload array expected by static/app.js.
    """
    # Dynamic import to safely capture your exact Job class structure dynamically
    try:
        from app.database import Job
    except ImportError:
        # Emergency local fallback declaration if dynamic import encounters path locks
        from sqlmodel import Field
        class Job(SQLModel, table=True):
            id: int | None = Field(default=None, primary_key=True)
            title: str
            company: str
            location: str = ""
            country: str = ""
            visa_sponsored: bool = False
            work_permit: bool = False
            relocation: bool = False

    try:
        with Session(engine) as session:
            # Query all jobs to compute baseline aggregate statistics
            all_jobs_statement = select(Job)
            all_jobs = session.exec(all_jobs_statement).all()
            
            # Apply frontend country filter drop-down variable if selected
            if country and country.strip() and country.lower() != "all countries":
                filtered_statement = select(Job).where(Job.country == country.strip())
                display_jobs = session.exec(filtered_statement).all()
            else:
                display_jobs = all_jobs

            # Construct structural response exactly how static/app.js interprets it
            response_payload = {
                "stats": {
                    "discovered": len(all_jobs),
                    "cv_matches": sum(1 for j in all_jobs if getattr(j, "cv_match", False) or getattr(j, "cv_match_pct", 0) > 70),
                    "visa_sponsored": sum(1 for j in all_jobs if getattr(j, "visa_sponsored", False)),
                    "work_permit": sum(1 for j in all_jobs if getattr(j, "work_permit", False)),
                    "relocation": sum(1 for j in all_jobs if getattr(j, "relocation", False))
                },
                "jobs": [
                    {
                        "id": job.id,
                        "title": job.title,
                        "company": job.company,
                        "location": job.location if job.location else "Remote / Global",
                        "country": job.country if job.country else "International",
                        "visa_sponsored": getattr(job, "visa_sponsored", False),
                        "work_permit": getattr(job, "work_permit", False),
                        "relocation": getattr(job, "relocation", False),
                        "url": getattr(job, "job_url", "#")
                    }
                    for job in display_jobs
                ]
            }
            return response_payload

    except Exception as exc:
        logger.error(f"API Route Engine Error: Failed to load payload: {exc}")
        # Safeguard fallback to keep the frontend running smoothly without 500 crashes
        return {
            "stats": {"discovered": 0, "cv_matches": 0, "visa_sponsored": 0, "work_permit": 0, "relocation": 0},
            "jobs": []
        }
