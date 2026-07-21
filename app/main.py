# app/main.py
"""
FastAPI Main Application Entrypoint.
Renders the Dashboard on the root endpoint and handles static assets.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import create_db_and_tables
from app.scheduler import start_scheduler
from app.api.jobs import router as jobs_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MainApp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB tables
    create_db_and_tables()

    # 2. Start APScheduler background tasks
    try:
        start_scheduler()
        logger.info("Scheduler started successfully.")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

    yield


app = FastAPI(title="Global Skilled Intelligence", lifespan=lifespan)

# Check 4: Mount static assets folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Check 3: Configure Jinja2 Templates directory
templates = Jinja2Templates(directory="app/templates")

# Register API Routers
app.include_router(jobs_router)


# Check 1 & 2: Root Endpoint renders dashboard.html
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    """
    Renders the Global Skilled Intelligence web dashboard.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})
