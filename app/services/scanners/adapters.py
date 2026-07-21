import logging
import httpx
import re
from sqlmodel import Session, select, SQLModel
from app.scoring import score_job

logger = logging.getLogger("SourceAdapters")

# ================================
# APPROVED HELPERS
# ================================

def _clean_html(raw_html: str) -> str:
    """Strips HTML tags and normalizes whitespace."""
    if not raw_html:
        return "No description available."
    clean_text = re.sub(r'<[^>]+>', ' ', str(raw_html))
    return " ".join(clean_text.split())

def _normalize_job_data(
    title: str = "Untitled Vacancy",
    company: str = "Verified Employer",
    country: str = "International",
    city: str = "Remote / Onsite",
    description: str = "",
    salary: str = "N/A",
    employment_type: str = "Full-time",
    job_url: str = "#",
    source_name: str = "Unknown Source",
    date_posted: str = "Recent"
) -> dict:
    """Strict Unified Adapter Schema (Zero field leakage)."""
    return {
        "title": title or "Untitled Vacancy",
        "company": company or "Verified Employer",
        "country": country or "International",
        "city": city or "Remote / Onsite",
        "description": _clean_html(description),
        "salary": salary or "N/A",
        "employment_type": employment_type or "Full-time",
        "job_url": job_url or "#",
        "source_name": source_name,
        "date_posted": date_posted or "Recent"
    }

# ================================
# GENERIC UNIFIED ADAPTER
# ================================

def execute_source_adapter(db: Session, source: dict) -> list:
    """
    Generic pipeline engine that handles unlimited public job sources.
    Uses registry parameters to fetch, normalize, and score records dynamically.
    """
    from app.database import Job, engine
    SQLModel.metadata.create_all(engine)

    source_name = source.get("name", "Unknown Source")
    api_url = source.get("api_url")
    target_country = source.get("country", "International")
    
    if not api_url:
        logger.error(f"Source [{source_name}] has no valid API URL configured.")
        return []

    try:
        headers = source.get("headers", {})
        params = source.get("params", {})
        response = httpx.get(api_url, headers=headers, params=params, timeout=15.0, follow_redirects=True)
        if response.status_code != 200:
            logger.warning(f"Source [{source_name}] returned HTTP {response.status_code}")
            return []
        
        payload = response.json()
    except Exception as network_err:
        logger.error(f"Network processing failed for source [{source_name}]: {network_err}")
        return []

    # Extract raw array dynamically using configured data key or default list fallbacks
    data_key = source.get("data_key")
    if data_key and isinstance(payload, dict):
        raw_listings = payload.get(data_key, [])
    elif isinstance(payload, list):
        raw_listings = payload
    elif isinstance(payload, dict):
        raw_listings = payload.get("data") or payload.get("jobs") or payload.get("items") or payload.get("stellenangebote") or []
    else:
        raw_listings = []

    new_inserted_jobs = []

    for raw_job in raw_listings:
        try:
            # Dynamic key extraction mapped against config
            title = raw_job.get(source.get("key_title", "title")) or raw_job.get("beruf") or "Untitled Vacancy"
            company = raw_job.get(source.get("key_company", "company_name")) or raw_job.get("employer_name") or raw_job.get("arbeitgeber") or "Verified Employer"
            location = raw_job.get(source.get("key_location", "location")) or raw_job.get("city") or "Remote / Onsite"
            job_url = raw_job.get(source.get("key_url", "url")) or "#"
            raw_desc = raw_job.get(source.get("key_description", "description")) or raw_job.get("summary") or ""

            # Standardized Normalization
            normalized = _normalize_job_data(
                title=title,
                company=company,
                country=target_country,
                city=str(location),
                description=raw_desc,
                salary=raw_job.get("salary", "N/A"),
                employment_type=raw_job.get("employment_type", "Full-time"),
                job_url=job_url,
                source_name=source_name,
                date_posted=raw_job.get("date_posted", "Recent")
            )

            # Strict Benefits Detection (Defaults strictly to False)
            combined_text = f"{normalized['title']} {normalized['description']}".lower()
            visa_sponsored = any(p in combined_text for p in ["visa sponsorship", "visa sponsor", "visa support"])
            work_permit = any(p in combined_text for p in ["work permit", "work permit support"])
            relocation = any(p in combined_text for p in ["relocation", "relocation package", "relocation assistance"])

            # Call Isolated Scoring Engine (Unpacks Dictionary Return)
            scores = score_job(
                title=normalized["title"],
                description=normalized["description"],
                visa=visa_sponsored,
                relocation=relocation
            )

            # Deduplication
            existing = db.exec(
                select(Job).where(Job.title == normalized["title"], Job.company == normalized["company"])
            ).first()
            
            if not existing:
                new_db_job = Job(
                    title=normalized["title"],
                    company=normalized["company"],
                    country=normalized["country"],
                    location=normalized["city"],
                    description=normalized["description"],
                    salary=normalized["salary"],
                    employment_type=normalized["employment_type"],
                    visa_sponsored=visa_sponsored,
                    work_permit=work_permit,
                    relocation=relocation,
                    cv_match=scores["cv_match"],
                    cv_match_pct=scores["cv_match_pct"],
                    api_score=scores["api_score"],
                    job_url=normalized["job_url"]
                )
                db.add(new_db_job)
                new_inserted_jobs.append(new_db_job)

        except Exception as item_err:
            logger.error(f"Error persisting item from [{source_name}]: {item_err}")
            continue

    if new_inserted_jobs:
        try:
            db.commit()
            logger.info(f"Source [{source_name}]: Successfully stored {len(new_inserted_jobs)} records.")
        except Exception as commit_err:
            logger.error(f"Database commit failed for [{source_name}]: {commit_err}")
            db.rollback()
            return []

    return new_inserted_jobs
