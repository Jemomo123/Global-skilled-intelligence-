import logging
from fastapi import APIRouter, Query
from sqlmodel import Session, select

from app.database import engine, Job

logger = logging.getLogger("GlobalApplicationJobsAPI")

router = APIRouter(
    prefix="/api",
    tags=["jobs"]
)

@router.get("/jobs")
def get_api_jobs(country: str = Query(None)):
    """Fetches and serializes stored job records for the frontend."""
    try:
        with Session(engine) as session:
            all_jobs = session.exec(select(Job)).all()
            
            if country and country.strip() and country.lower() != "all countries":
                display_jobs = session.exec(
                    select(Job).where(Job.country == country.strip())
                ).all()
            else:
                display_jobs = all_jobs

            formatted_jobs = []
            for job in display_jobs:
                job_link = getattr(job, "job_url", None) or getattr(job, "url", "#")
                
                formatted_jobs.append({
                    "id": getattr(job, "id", None),
                    "title": getattr(job, "title", "Untitled Position"),
                    "company": getattr(job, "company", "Discovered Employer"),
                    "location": getattr(job, "location", "Remote / Global"),
                    "country": getattr(job, "country", "International"),
                    "description": getattr(job, "description", "No description available."),
                    "salary": getattr(job, "salary", "N/A"),
                    "employment_type": getattr(job, "job_type", None) or getattr(job, "employment_type", "Full-time"),
                    "date_discovered": getattr(job, "created_at", None) or getattr(job, "date_discovered", None),
                    "api_score": getattr(job, "api_score", 0),
                    "cv_match": bool(getattr(job, "cv_match", False)),
                    "cv_match_pct": getattr(job, "cv_match_pct", 0),
                    "visa_sponsored": bool(getattr(job, "visa_sponsored", False)),
                    "work_permit": bool(getattr(job, "work_permit", False)),
                    "relocation": bool(getattr(job, "relocation", False)),
                    "url": job_link,
                    "job_url": job_link
                })

            return {
                "stats": {
                    "discovered": len(all_jobs),
                    "cv_matches": sum(1 for j in formatted_jobs if j["cv_match"]),
                    "visa_sponsored": sum(1 for j in formatted_jobs if j["visa_sponsored"]),
                    "work_permit": sum(1 for j in formatted_jobs if j["work_permit"]),
                    "relocation": sum(1 for j in formatted_jobs if j["relocation"])
                },
                "jobs": formatted_jobs
            }
            
    except Exception as exc:
        logger.error(f"Modular Jobs API Failure: {exc}", exc_info=True)
        return {
            "stats": {"discovered": 0, "cv_matches": 0, "visa_sponsored": 0, "work_permit": 0, "relocation": 0},
            "jobs": []
        }
