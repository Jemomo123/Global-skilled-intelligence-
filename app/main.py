import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.scheduler import start_scheduler
from app.api.health import router as health_router
from app.api.jobs import router as jobs_router  # Include the brought back file

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

# Core Path Declarations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

try:
    if os.path.exists(STATIC_DIR):
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
except Exception as e:
    logger.warning(f"Static directory mounting skipped: {e}")

# Register all production API modular routing interfaces
app.include_router(health_router)
app.include_router(jobs_router)

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI Lifecycle: Initializing system startup routing...")
    start_scheduler()
    logger.info("FastAPI Lifecycle: Startup sequence fully completed.")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    Authoritative root endpoint rendering the dashboard interface.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/status")
def read_status():
    """
    Preserves the raw JSON metadata status string for health checks.
    """
    return {"status": "online", "framework": "Phase 2 Production Modular"}
