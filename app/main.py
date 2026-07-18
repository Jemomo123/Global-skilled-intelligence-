from fastapi import FastAPI, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, desc
from typing import Optional, List
from datetime import datetime, timezone

from app.database import init_db, get_db
from app.models import Job
from app.scheduler import start_scheduler, run_global_scanners

app = FastAPI(title="Global Skilled Intelligence Portal")

# Mount static folder for CSS and JavaScript
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize Jinja2 templates directory matching the repository structure
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """
    Production monitoring health check verifying database availability and pipeline operational state.
    """
    try:
        db.execute(select(1))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, 503

@app.get("/api/jobs")
def get_jobs_api(
    db: Session = Depends(get_db),
    country: Optional[str] = Query(None, description="Filter by country"),
    trade: Optional[str] = Query(None, description="Filter by active trade keyword"),
    visa_sponsored: Optional[bool] = Query(None, description="Filter by visa sponsorship"),
    work_permit: Optional[bool] = Query(None, description="Filter by work permit support"),
    relocation: Optional[bool] = Query(None, description="Filter by relocation assistance"),
    min_score: Optional[int] = Query(None, description="Filter by minimum API score"),
    min_cv_match: Optional[int] = Query(None, description="Filter by minimum CV match percentage"),
    sort_by: Optional[str] = Query("highest_score", description="Sort criteria")
):
    """
    Fetches discovered live jobs from the database, applying advanced multi-tier filtering 
    and multi-mode sorting parameters.
    """
    statement = select(Job)
    
    # Apply filters
    if country and country.lower() != "all countries":
        statement = statement.where(Job.country == country)
        
    if trade:
        statement = statement.where(
            (Job.title.ilike(f"%{trade}%")) | (Job.description.ilike(f"%{trade}%"))
        )
        
    if visa_sponsored is not None:
        statement = statement.where(Job.visa_sponsored == visa_sponsored)
        
    if work_permit is not None:
        statement = statement.where(Job.work_permit == work_permit)
        
    if relocation is not None:
        statement = statement.where(Job.relocation == relocation)
        
    if min_score is not None:
        statement = statement.where(Job.api_score >= min_score)
        
    if min_cv_match is not None:
        statement = statement.where(Job.cv_match_pct >= min_cv_match)

    # Dynamic sorting implementation (Priority 6)
    if sort_by == "highest_score":
        statement = statement.order_by(desc(Job.api_score))
    elif sort_by == "highest_cv":
        statement = statement.order_by(desc(Job.cv_match_pct))
    elif sort_by == "newest":
        statement = statement.order_by(desc(Job.date_discovered))
    elif sort_by == "country":
        statement = statement.order_by(Job.country)
    elif sort_by == "employer":
        statement = statement.order_by(Job.company)
    else:
        statement = statement.order_by(desc(Job.api_score))

    jobs = db.exec(statement).all()
    
    processed_jobs = []
    for job in jobs:
        job_dict = job.dict()
        if job_dict.get("city") and job_dict.get("country"):
            job_dict["location"] = f"{job_dict['city']}, {job_dict['country']}"
        else:
            job_dict["location"] = job_dict.get("location") or f"{job_dict.get('country', 'Skilled Region')}"
        processed_jobs.append(job_dict)
        
    return processed_jobs

@app.on_event("startup")
def on_startup():
    init_db()
    run_global_scanners()
    start_scheduler()
    
