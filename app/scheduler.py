import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.services.scanners.scanner_core import run_global_scanner

logger = logging.getLogger("ApplicationScheduler")
scheduler = BackgroundScheduler()

def scheduled_production_scanner_job():
    """
    Unified Production Entry Point.
    Executes the strategy-agnostic scanner loop.
    """
    logger.info("APScheduler: Launching unified global scan loop...")
    db = SessionLocal()
    try:
        new_jobs_count = run_global_scanner(db)
        logger.info(f"APScheduler: Global scan complete. Newly stored jobs: {new_jobs_count}")
    except Exception as e:
        logger.error(f"APScheduler: Global scan job encountered an error: {e}")
    finally:
        db.close()

def start_scheduler():
    """Initializes and activates the single unified production job."""
    if not scheduler.running:
        # Executes every 30 minutes to look for new targets
        scheduler.add_job(
            scheduled_production_scanner_job,
            'interval',
            minutes=30,
            id='unified_global_scanner',
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler: Production Background Service Activated.")
