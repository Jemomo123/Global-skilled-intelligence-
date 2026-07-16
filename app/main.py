from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from app.schemas import EnrichedJob
from app.services.discovery.engine import DiscoveryEngine

app = FastAPI(title="Global Skilled Intelligence API")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
discovery_engine = DiscoveryEngine()

@app.get("/", response_class=HTMLResponse)
def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/status")
def api_status():
    return {
        "status": "online",
        "message": "Welcome to the Global Skilled Intelligence API!"
    }

@app.get("/api/jobs/discover", response_model=List[EnrichedJob])
def discover_jobs():
    """Runs the discovery process, applying full backend intelligence models."""
    jobs = discovery_engine.run_all()
    return jobs
