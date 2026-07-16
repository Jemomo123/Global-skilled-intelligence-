from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select, desc
import os

from app.database import init_db, get_db
from app.models import Job
from app.scheduler import start_scheduler, run_global_scanners

app = FastAPI(title="Global Skilled Intelligence Portal")

# Mount Static Assets (app.js, style.css)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve your home page index.html when someone visits the website
@app.get("/")
def read_root():
    # Looks for index.html inside app/templates/ or app/static/ or the root folder
    possible_paths = [
        "app/templates/index.html",
        "app/static/index.html",
        "app/index.html",
        "index.html"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return FileResponse(path)
    return {"error": "index.html not found. Please ensure it is placed in app/templates/ or app/static/"}

# Serve the live database jobs
@app.get("/api/jobs")
def get_jobs_api(db: Session = Depends(get_db)):
    statement = select(Job).order_by(desc(Job.api_score))
    jobs = db.exec(statement).all()
    return jobs

@app.on_event("startup")
def on_startup():
    # 1. Initialize SQLite database and tables
    init_db()
    # 2. Trigger an immediate scan on startup
    run_global_scanners()
    # 3. Start the background scheduler
    start_scheduler()
