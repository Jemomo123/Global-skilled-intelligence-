import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session
from app.database import engine
from app.services.scanners.scanner_core import run_global_scanner

logger = logging.getLogger("ApplicationScheduler")
scheduler = BackgroundScheduler()

def scheduled_production_scanner_job():
    """
    Unified Production Entry Point.
    Executes the global scan using native SQLModel context management.
    """
    logger.info("APScheduler: Launching unified global scan loop...")
    try:
        with Session(engine) as db:
            new_jobs_count = run_global_scanner(db)
            logger.info(f"APScheduler: Global scan complete. Newly stored jobs: {new_jobs_count}")
    except Exception as e:
        logger.error(f"APScheduler: Global scan job encountered an error: {e}")

def start_scheduler():
    """Initializes and activates the single unified production job."""
    if not scheduler.running:
        scheduler.add_job(
            scheduled_production_scanner_job,
            'interval',
            minutes=30,
            id='unified_global_scanner',
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler: Production Background Service Activated.")
