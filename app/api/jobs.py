# app/api/jobs.py
"""
Jobs REST API Endpoint.

Handles job retrieval, country filtering, stats aggregation, sorting, and pagination.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Query, Depends
from sqlmodel import Session, select, func, case, cast, Integer

from app.database import get_db, Job

logger = logging.getLogger("GlobalApplicationJobsAPI")

router = APIRouter(
    prefix="/api",
    tags=["jobs"]
)


@router.get("/jobs")
def get_api_jobs(
    country: Optional[str] = Query(None),
    cv_match_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """Fetches and serializes stored job records with single-query efficiency and pagination."""
    try:
        # Base filtered query
        base_query = select(Job)
        
        if country and country.strip() and country.lower() != "all countries":
            base_query = base_query.where(Job.country == country.strip())
            
        if cv_match_only:
            base_query = base_query.where(Job.cv_match == True)

        # 1. Single Query Stats Aggregation
        stats_query = select(
            func.count(Job.id).label("discovered"),
            func.sum(cast(Job.cv_match, Integer)).label("cv_matches"),
            func.sum(cast(Job.visa_sponsored, Integer)).label("visa_sponsored"),
            func.sum(cast(Job.work_permit, Integer)).label("work_permit"),
            func.sum(cast(Job.relocation, Integer)).label("relocation")
        )
        
        if country and country.strip() and country.lower() != "all countries":
            stats_query = stats_query.where(Job.country == country.strip())

        stats_result = db.exec(stats_query).first()

        stats = {
            "discovered": stats_result[0] or 0,
            "cv_matches": stats_result[1] or 0,
            "visa_sponsored": stats_result[2] or 0,
            "work_permit": stats_result[3] or 0,
            "relocation": stats_result[4] or 0,
        }

        # 2. Paginated & Sorted Query (Newest First via Job.id.desc())
        paginated_query = base_query.order_by(Job.id.desc()).offset(offset).limit(limit)
        jobs_list = db.exec(paginated_query).all()

        formatted_jobs = []
        for job in jobs_list:
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
            "stats": stats,
            "jobs": formatted_jobs,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "count": len(formatted_jobs)
            }
        }
            
    except Exception as exc:
        logger.error(f"Modular Jobs API Failure: {exc}", exc_info=True)
        return {
            "stats": {"discovered": 0, "cv_matches": 0, "visa_sponsored": 0, "work_permit": 0, "relocation": 0},
            "jobs": [],
            "pagination": {"limit": limit, "offset": offset, "count": 0}
        }
