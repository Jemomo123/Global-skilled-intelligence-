import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.scheduler import start_scheduler
from app.api.health import router as health_router
from app.api.jobs import router as jobs_router

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

try:
    if os.path.exists(STATIC_DIR):
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
except Exception as e:
    logger.warning(f"Static directory mounting skipped: {e}")

app.include_router(health_router)
app.include_router(jobs_router)

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI Lifecycle: Initializing system startup routing...")
    
    # Start background loop
    start_scheduler()
    
    # STEP 5: Force manual diagnostic run inline right now during startup
    try:
        logger.info("DEBUG PIPELINE: Executing manual startup diagnostic scan...")
        from app.scanner_core import run_global_scanner
        
        # This executes your exact baseline processing routine immediately
        run_global_scanner()
        logger.info("DEBUG PIPELINE: Manual startup diagnostic scan execution completed successfully.")
    except Exception as pipeline_err:
        logger.error(f"DEBUG PIPELINE: Emergency manual execution bypassed: {pipeline_err}")

    logger.info("FastAPI Lifecycle: Startup sequence fully completed.")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/status")
def read_status():
    return {"status": "online", "framework": "Phase 3 Production Modular Pipeline Debug"}
    
