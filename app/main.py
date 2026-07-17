from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, desc
import os

from app.database import init_db, get_db
from app.models import Job
from app.scheduler import start_scheduler, run_global_scanners

app = FastAPI(title="Global Skilled Intelligence Portal")

# Dynamically resolve absolute paths relative to app/main.py location
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "templates")

# Mount static folder cleanly using robust path resolution
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize Jinja2 templates directory robustly
if os.path.exists(TEMPLATES_DIR):
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
else:
    templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def read_root(request: Request):
    # Standard template invocation compatible with starlette environment specifications
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/jobs")
def get_jobs_api(db: Session = Depends(get_db)):
    statement = select(Job).order_by(desc(Job.api_score))
    jobs = db.exec(statement).all()
    return jobs

@app.on_event("startup")
def on_startup():
    # --- FRONTEND ASSET AUDIT LOGS ---
    print("--- RENDER DEPLOYMENT FILE SYSTEM AUDIT ---")
    print(f"Main File Location: {__file__}")
    print(f"Target Templates Absolute Path: {TEMPLATES_DIR} (Exists: {os.path.exists(TEMPLATES_DIR)})")
    print(f"Target Static Absolute Path: {STATIC_DIR} (Exists: {os.path.exists(STATIC_DIR)})")
    if os.path.exists(TEMPLATES_DIR):
        print(f"Contents of templates folder: {os.listdir(TEMPLATES_DIR)}")
    print("-------------------------------------------")
    
    init_db()
    run_global_scanners()
    start_scheduler()
