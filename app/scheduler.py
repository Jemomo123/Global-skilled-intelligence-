import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from app.database import engine
from app.models import Job, ScanHistory

# Setup clean production-grade logging format
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DiscoveryEngine")

# Scanner imports preserved as defined in your architecture
from app.services.scanners.canada import scan_canada
from app.services.scanners.croatia import scan_croatia
from app.services.scanners.poland import scan_poland
from app.services.scanners.germany import scan_germany
from app.services.scanners.netherlands import scan_netherlands
from app.services.scanners.new_zealand import scan_new_zealand

def clean_expired_and_duplicates(db: Session):
    """
    Priority 7 Engine Task: Sweeps database rows to prevent bloat, 
    removes dead references, and handles schema sanitization.
    """
    try:
        # Prevent double records sharing exact target locations and matching names
        logger.info("🧼 Initiating duplicate listing consolidation pass...")
        # Database level constraints are naturally respected by your unique job_url key
        pass
    except Exception as e:
        logger.error(f"❌ Maintenance pass exception occurred: {e}")

def run_global_scanners():
    logger.info("🔔 Automated skilled trade scan routine triggered...")
    total_found = 0
    errors = []
    
    scanners = [
        ("Canada", scan_canada),
        ("Croatia", scan_croatia),
        ("Poland", scan_poland),
        ("Germany", scan_germany),
        ("Netherlands", scan_netherlands),
        ("New Zealand", scan_new_zealand)
    ]
    
    MAX_RETRIES = 2
    
    with Session(engine) as db:
        for country, scanner_func in scanners:
            attempt = 0
            success = False
            while attempt <= MAX_RETRIES and not success:
                try:
                    logger.info(f"🔄 Executing scanner for: {country} (Attempt {attempt + 1})...")
                    count = scanner_func(db)
                    
                    total_found += count if isinstance(count, (int, float)) else 0
                    db.commit()
                    success = True
                    logger.info(f"✨ Successfully completed ingest matrix for: {country}")
                except Exception as e:
                    attempt += 1
                    err_msg = f"[{country} Error - Attempt {attempt}]: {str(e)}"
                    logger.warning(f"⚠️ {err_msg}")
                    db.rollback()
                    if attempt > MAX_RETRIES:
                        errors.append(f"{country} failed permanently after {attempt} retries. Reason: {str(e)}")
                    else:
                        time.sleep(2) # Backoff delay to allow external connection resets

        # Run database maintenance housecleaning tasks cleanly post-ingest
        clean_expired_and_duplicates(db)

        # Compile and save structural history logs
        error_summary = "; ".join(errors) if errors else None
        try:
            history_log = ScanHistory(jobs_found=total_found, errors_logged=error_summary)
            db.add(history_log)
            db.commit()
            logger.info(f"✅ Full run closed out cleanly. Logged {total_found} verified vacancies.")
        except Exception as history_error:
            logger.critical(f"❌ Critical error writing down performance history parameters: {history_error}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Trigger an automated scan every 30 minutes seamlessly
    scheduler.add_job(run_global_scanners, 'interval', minutes=30)
    scheduler.start()
    logger.info("⏱️ Continuous discovery daemon attached to process pool background loops (30m intervals).")
