import logging
import os
from fastapi import APIRouter, Query
from sqlmodel import Session, create_engine, select, SQLModel

logger = logging.getLogger("GlobalApplicationJobsAPI")

router = APIRouter(
    prefix="/api",
    tags=["jobs"]
)

# Unified single production database engine allocation matrix
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jobs.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

@router.get("/jobs")
def get_api_jobs(country: str = Query(None)):
    """
    Fetches raw jobs and prints pipeline transmission logs safely.
    """
        from app.database import Job


    try:
        with Session(engine) as session:
            all_jobs = session.exec(select(Job)).all()
            
            if country and country.strip() and country.lower() != "all countries":
                display_jobs = session.exec(select(Job).where(Job.country == country.strip())).all()
            else:
                display_jobs = all_jobs

            print(f"DEBUG PIPELINE: Returning {len(display_jobs)} jobs to API response context")

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
