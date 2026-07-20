import logging
from fastapi import APIRouter, Query
from sqlmodel import Session, select

# Centralized authoritative database engine reference synchronization
from app.database import engine, Job

logger = logging.getLogger("GlobalApplicationJobsAPI")

router = APIRouter(
    prefix="/api",
    tags=["jobs"]
)

@router.get("/jobs")
def get_api_jobs(country: str = Query(None)):
    """
    Fetches raw jobs and prints pipeline transmission logs safely.
    """
    try:
        with Session(engine) as session:
            all_jobs = session.exec(select(Job)).all()
            
            if country and country.strip() and country.lower() != "all countries":
                display_jobs = session.exec(
                    select(Job).where(Job.country == country.strip())
                ).all()
            else:
                display_jobs = all_jobs

            logger.info(f"DEBUG PIPELINE: Returning {len(display_jobs)} jobs out of {len(all_jobs)} total.")

            formatted_jobs = []
            for job in display_jobs:
                # Safely resolve URL from either attribute variant
                job_link = getattr(job, "job_url", None) or getattr(job, "url", "#")
                
                formatted_jobs.append({
                    "id": getattr(job, "id", None),
                    "title": getattr(job, "title", "Untitled Position"),
                    "company": getattr(job, "company", "Discovered Employer"),
                    "location": getattr(job, "location", "Remote / Global"),
                    "country": getattr(job, "country", "International"),
                    "visa_sponsored": bool(getattr(job, "visa_sponsored", False)),
                    "work_permit": bool(getattr(job, "work_permit", False)),
                    "relocation": bool(getattr(job, "relocation", False)),
                    "url": job_link,
                    "job_url": job_link
                })

            return {
                "stats": {
                    "discovered": len(all_jobs),
                    "cv_matches": sum(1 for j in all_jobs if getattr(j, "cv_match", False) or getattr(j, "cv_match_pct", 0) > 70),
                    "visa_sponsored": sum(1 for j in all_jobs if getattr(j, "visa_sponsored", False)),
                    "work_permit": sum(1 for j in all_jobs if getattr(j, "work_permit", False)),
                    "relocation": sum(1 for j in all_jobs if getattr(j, "relocation", False))
                },
                "jobs": formatted_jobs
            }
            
    except Exception as exc:
        logger.error(f"Modular Jobs API Failure: {exc}", exc_info=True)
        return {
            "stats": {"discovered": 0, "cv_matches": 0, "visa_sponsored": 0, "work_permit": 0, "relocation": 0},
            "jobs": []
        }
