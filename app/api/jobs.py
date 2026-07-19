import logging
import os
from fastapi import APIRouter, Query
from sqlmodel import Session, create_engine, select

# Setup localized logging
logger = logging.getLogger("GlobalApplicationJobsAPI")

router = APIRouter(
    prefix="/api",
    tags=["jobs"]
)

# Database Setup matching production config
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jobs.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

@router.get("/jobs")
def get_api_jobs(country: str = Query(None)):
    """
    Modular route handler fetching vacancies directly from SQLModel 
    and returning the payload formatting requested by the frontend.
    """
    try:
        from app.database import Job
    except ImportError:
        from sqlmodel import SQLModel, Field
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
            all_jobs = session.exec(select(Job)).all()
            
            if country and country.strip() and country.lower() != "all countries":
                display_jobs = session.exec(select(Job).where(Job.country == country.strip())).all()
            else:
                display_jobs = all_jobs

            return {
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
    except Exception as exc:
        logger.error(f"Modular Jobs API Failure: {exc}")
        return {
            "stats": {"discovered": 0, "cv_matches": 0, "visa_sponsored": 0, "work_permit": 0, "relocation": 0},
            "jobs": []
        }
