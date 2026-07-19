import logging
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

# Configure Template and Static files rendering engines
templates = Jinja2Templates(directory="templates")
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Static directory mounting skipped or not found: {e}")

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
