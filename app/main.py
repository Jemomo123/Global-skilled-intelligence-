from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select, desc

from app.database import init_db, get_db
from app.models import Job
from app.scheduler import start_scheduler, run_global_scanners

app = FastAPI(title="Global Skilled Intelligence Portal")

# Mount Static Assets (so app.js and style.css load perfectly on mobile)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def on_startup():
    # 1. Initialize SQLite database and tables
    init_db()
    # 2. Trigger an immediate scan on startup so the database has jobs ready
    run_global_scanners()
    # 3. Start the background scheduler
    start_scheduler()

# This API route now serves live database jobs ordered by their matching score!
@app.get("/api/jobs")
def get_jobs_api(db: Session = Depends(get_db)):
    statement = select(Job).order_by(desc(Job.api_score))
    jobs = db.exec(statement).all()
    return jobs
