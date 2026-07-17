from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, desc

from app.database import init_db, get_db
from app.models import Job
from app.scheduler import start_scheduler, run_global_scanners

app = FastAPI(title="Global Skilled Intelligence Portal")

# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize Jinja2 templates directory
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



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
