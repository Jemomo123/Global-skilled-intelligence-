# app/main.py
"""
FastAPI Main Application Entrypoint.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import create_db_and_tables
from app.scheduler import start_scheduler
from app.api.jobs import router as jobs_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MainApp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create database tables BEFORE starting scheduler
    create_db_and_tables()

    # 2. Start Scheduler
    try:
        start_scheduler()
        logger.info("Scheduler started successfully.")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

    yield


app = FastAPI(title="Global Skilled Intelligence", lifespan=lifespan)

# Register API Routers
app.include_router(jobs_router)


@app.get("/")
def read_root():
    return {"message": "Global Skilled Intelligence API is live."}
