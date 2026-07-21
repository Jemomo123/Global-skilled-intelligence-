# app/scheduler.py
"""
APScheduler Background Task Manager.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.scanners.scanner_core import run_global_scanner

logger = logging.getLogger("Scheduler")

scheduler = BackgroundScheduler()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            run_global_scanner,
            'interval',
            hours=1,
            id='global_scanner_job',
            replace_existing=True
        )
        scheduler.start()
        logger.info("Background scheduler started.")
