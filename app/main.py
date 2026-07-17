from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, desc
import os

from app.database import init_db, get_db
from app.models import Job
from app.scheduler import start_scheduler, run_global_scanners

app = FastAPI(title="Global Skilled Intelligence Portal")

# Mount static folder cleanly
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Fallback template definition if needed elsewhere
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    # Search paths for index.html to ensure it loads regardless of structure
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "templates", "index.html"),
        os.path.join(os.path.dirname(__file__), "static", "index.html"),
        "app/templates/index.html",
        "app/static/index.html",
        "templates/index.html",
        "index.html"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
                
    # If the file is completely missing from deployment, give a clear structural report
    cwd_contents = os.listdir(".")
    app_contents = os.listdir("app") if os.path.exists("app") else []
    return PlainTextResponse(
        f"Error: 'index.html' not found in deployment.\n"
        f"Current Working Directory: {os.getcwd()}\n"
        f"Root Contents: {cwd_contents}\n"
        f"App Contents: {app_contents}", 
        status_code=404
    )

@app.get("/api/jobs")
def get_jobs_api(db: Session = Depends(get_db)):
    statement = select(Job).order_by(desc(Job.api_score))
    jobs = db.exec(statement).all()
    return jobs

@app.on_event("startup")
def on_startup():
    init_db()
    run_global_scanners()
    start_scheduler()
