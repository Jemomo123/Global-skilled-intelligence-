# adapters.py
import logging
import httpx
import re
from sqlmodel import Session, select, SQLModel

logger = logging.getLogger("SourceAdapters")

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return "No description available."
    clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
    return " ".join(clean_text.split())

def execute_source_adapter(db: Session, source: dict) -> list:
    from app.database import Job, engine
    SQLModel.metadata.create_all(engine)

    source_name = source.get("name", "Unknown Source")
    api_url = source.get("api_url")
    target_country = source.get("country", "International")
    
    new_inserted_jobs = []
    
    try:
        response = httpx.get(api_url, timeout=15.0, follow_redirects=True)
        if response.status_code != 200:
            return []
        payload = response.json()
    except Exception as network_err:
        logger.error(f"Network processing failed for source {source_name}: {network_err}")
        return []

    raw_listings = payload.get("data", []) if isinstance(payload, dict) else []

    for raw_job in raw_listings:
        try:
            title = raw_job.get("title", "Untitled Vacancy")
            company = raw_job.get("company_name", "Discovered Employer")
            location = raw_job.get("location", "Remote / Onsite")
            job_url = raw_job.get("url", "#")
            raw_desc = raw_job.get("description", "")
            
            clean_desc = clean_html(raw_desc)
            tags = [str(t).lower() for t in raw_job.get("tags", [])]
            combined_text = f"{title.lower()} {clean_desc.lower()} {' '.join(tags)}"

            # Strict explicit keyword verification (Defaults strictly to False)
            visa_sponsored = any(p in combined_text for p in ["visa sponsorship", "visa sponsor", "visa support"])
            work_permit = any(p in combined_text for p in ["work permit", "work permit support"])
            relocation = any(p in combined_text for p in ["relocation", "relocation package", "relocation assistance"])

            # Deduplication check
            existing = db.exec(
                select(Job).where(Job.title == title, Job.company == company)
            ).first()
            
            if not existing:
                new_db_job = Job(
                    title=title,
                    company=company,
                    location=location,
                    country=target_country,
                    description=clean_desc,
                    visa_sponsored=visa_sponsored,
                    work_permit=work_permit,
                    relocation=relocation,
                    job_url=job_url
                )
                db.add(new_db_job)
                new_inserted_jobs.append(new_db_job)
                
        except Exception as item_err:
            logger.error(f"Error processing item: {item_err}")
            continue

    if new_inserted_jobs:
        try:
            db.commit()
            logger.info(f"Source {source_name}: {len(new_inserted_jobs)} jobs stored successfully.")
        except Exception as commit_err:
            logger.error(f"Database commit failed: {commit_err}")
            db.rollback()
            return []
            
    return new_inserted_jobs
