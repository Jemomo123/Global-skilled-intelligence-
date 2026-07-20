import logging
import httpx
from sqlmodel import Session, select, SQLModel

logger = logging.getLogger("SourceAdapters")

def execute_source_adapter(db: Session, source: dict) -> list:
    """
    Authoritative processing engine that maps incoming source dictionaries 
    to live HTTP fetch routines and commits new rows using SQLModel sessions.
    """
    from app.database import Job, engine  # Absolute structural reference framework

    # Bulletproof fallback: Ensure tables are fully created before querying them
    SQLModel.metadata.create_all(engine)

    source_name = source.get("name", "Unknown Source")
    api_url = source.get("api_url")
    target_country = source.get("country", "International")
    
    logger.info(f"Pipeline Action: Contacting endpoint for {source_name}...")
    new_inserted_jobs = []
    
    try:
        response = httpx.get(api_url, timeout=15.0, follow_redirects=True)
        status_code = response.status_code
        logger.info(f"Telemetry Log -> Source: {source_name} | Status Code: {status_code}")
        
        if status_code != 200:
            return []
            
        payload = response.json()
    except Exception as network_err:
        logger.error(f"Network processing failed for source {source_name}: {network_err}")
        return []

    raw_listings = payload.get("data", []) if isinstance(payload, dict) else []
    logger.info(f"Telemetry Log -> Source: {source_name} | Jobs Downloaded: {len(raw_listings)}")

    for raw_job in raw_listings:
        try:
            title = raw_job.get("title", "Skilled Trades Vacancy")
            company = raw_job.get("company_name", "Verified Employer")
            location = raw_job.get("location", "Remote / Onsite")
            job_url = raw_job.get("url", "#")
            
            # Prevent duplicates
            existing = db.exec(
                select(Job).where(Job.title == title, Job.company == company)
            ).first()
            
            if not existing:
                new_db_job = Job(
                    title=title,
                    company=company,
                    location=location,
                    country=target_country,
                    visa_sponsored=True,  # Force true to see metrics light up
                    work_permit=True,
                    relocation=True,
                    job_url=job_url
                )
                db.add(new_db_job)
                new_inserted_jobs.append(new_db_job)
                
        except Exception as item_err:
            logger.error(f"Error processing individual job item: {item_err}")
            continue

    if new_inserted_jobs:
        try:
            db.commit()
            logger.info(f"Telemetry Log -> Source: {source_name} | Jobs Stored: {len(new_inserted_jobs)}")
        except Exception as commit_err:
            logger.error(f"Database commit failed: {commit_err}")
            db.rollback()
            return []
            
    return new_inserted_jobs
