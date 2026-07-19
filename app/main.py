import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.scheduler import start_scheduler
from app.api.health import router as health_router

# Setup unified application logging matrix
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GlobalApplicationMain")

app = FastAPI(
    title="Global Skilled Intelligence",
    description="Skilled trade intelligence & live discovery service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamically build absolute paths relative to this file's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # /opt/render/project/src/app
PROJECT_ROOT = os.path.dirname(BASE_DIR)              # /opt/render/project/src

search_paths = [
    os.path.join(PROJECT_ROOT, "templates"),
    PROJECT_ROOT,
    os.path.join(BASE_DIR, "templates"),
    BASE_DIR
]

logger.info(f"Configuring Jinja2 search paths: {search_paths}")
templates = Jinja2Templates(directory=search_paths)

try:
    app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_ROOT, "static")), name="static")
except Exception as e:
    try:
        app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
    except Exception as static_err:
        logger.warning(f"Static directory mounting skipped or not found: {static_err}")

# Register the production API routing interfaces
app.include_router(health_router)

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI Lifecycle: Initializing system startup routing...")
    # Clean handoff to the single background scheduler
    start_scheduler()
    logger.info("FastAPI Lifecycle: Startup sequence fully completed.")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    Authoritative root endpoint rendering the dashboard interface.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/status")
def read_status():
    """
    Preserves the raw JSON metadata status string for health checks.
    """
    return {"status": "online", "framework": "Phase 2 Production Modular"}
