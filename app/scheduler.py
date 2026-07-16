from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session
from app.database import engine
from app.models import ScanHistory
from app.services.scanners.canada import scan_canada
from app.services.scanners.croatia import scan_croatia
from app.services.scanners.poland import scan_poland
from app.services.scanners.germany import scan_germany
from app.services.scanners.netherlands import scan_netherlands
from app.services.scanners.new_zealand import scan_new_zealand

def run_global_scanners():
    print("🔔 Automated scan routine triggered...")
    total_found = 0
    error_message = None
    
    with Session(engine) as db:
        try:
            total_found += scan_canada(db)
            total_found += scan_croatia(db)
            total_found += scan_poland(db)
            total_found += scan_germany(db)
            total_found += scan_netherlands(db)
            total_found += scan_new_zealand(db)
        except Exception as e:
            error_message = str(e)
            print(f"❌ Error during automated scanning cycle: {e}")

        # Save performance record to history table
        history_log = ScanHistory(jobs_found=total_found, errors_logged=error_message)
        db.add(history_log)
        db.commit()
        print(f"✅ Scan finished. Saved {total_found} fresh matching items.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Trigger an automated scan every 30 minutes
    scheduler.add_job(run_global_scanners, 'interval', minutes=30)
    scheduler.start()
