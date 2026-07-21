# app/main.py
"""
FastAPI Main Application Entrypoint.
Renders the Dashboard on root and executes an immediate global scan on startup.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import create_db_and_tables, engine
from app.scheduler import start_scheduler
from app.services.scanners.scanner_core import run_global_scanner
from app.api.jobs import router as jobs_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MainApp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB tables
    logger.info("[STARTUP] Initializing database tables...")
    create_db_and_tables()

    # 2. Start Background Scheduler
    try:
        start_scheduler()
        logger.info("[STARTUP] APScheduler initialized.")
    except Exception as e:
        logger.error(f"[STARTUP] Failed to start scheduler: {e}")

    # 3. TASK 2: Execute an immediate global scan on startup without waiting for timer
    logger.info("[STARTUP] Triggering immediate production global scanning sequence...")
    try:
        run_global_scanner()
        logger.info("[STARTUP] Initial global scan trigger completed.")
    except Exception as e:
        logger.error(f"[STARTUP] Direct global scan execution failed: {e}", exc_info=True)

    yield


app = FastAPI(title="Global Skilled Intelligence", lifespan=lifespan)

# Static assets & Jinja templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Register API Routers
app.include_router(jobs_router)


@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
