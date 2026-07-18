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
    errors = []
    
    # List of all scanner operations to execute independently
    scanners = [
        ("Canada", scan_canada),
        ("Croatia", scan_croatia),
        ("Poland", scan_poland),
        ("Germany", scan_germany),
        ("Netherlands", scan_netherlands),
        ("New Zealand", scan_new_zealand)
    ]
    
    with Session(engine) as db:
        for country, scanner_func in scanners:
            try:
                print(f"🔄 Executing scanner for: {country}...")
                count = scanner_func(db)
                # Safely guarantee we parse an integer return value
                total_found += count if isinstance(count, (int, float)) else 0
                db.commit() # Flush and save this specific country's batch immediately
            except Exception as e:
                err_msg = f"[{country} Error]: {str(e)}"
                print(f"❌ {err_msg}")
                errors.append(err_msg)
                db.rollback() # Undo any corrupt session state for this country only

        # Compile final status report
        error_summary = "; ".join(errors) if errors else None

        # Save performance record to history table safely
        try:
            history_log = ScanHistory(jobs_found=total_found, errors_logged=error_summary)
            db.add(history_log)
            db.commit()
            print(f"✅ Scan finished completely. Saved {total_found} fresh matching items across all online regions.")
        except Exception as history_error:
            print(f"⚠️ Failed to write to ScanHistory table: {history_error}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Trigger an automated scan every 30 minutes
    scheduler.add_job(run_global_scanners, 'interval', minutes=30)
    scheduler.start()
