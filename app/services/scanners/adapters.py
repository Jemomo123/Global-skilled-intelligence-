import logging
import httpx
import re
from sqlmodel import Session, select, SQLModel

logger = logging.getLogger("SourceAdapters")

# Trade Keywords & Exclusions
SKILLED_TRADE_KEYWORDS = [
    "plumber", "plumbing", "pipefitter", "pipe fitter", "mechanical fitter",
    "fitter", "hvac", "welder", "welding", "electrician", "electrical",
    "construction maintenance", "industrial maintenance", "maintenance technician",
    "mechanical technician"
]

EXCLUDED_KEYWORDS = [
    "software", "ai engineer", "data engineer", "marketing", "sales", 
    "human resources", "hr", "finance", "commercial director", "accountant"
]


def _clean_html(raw_html: str) -> str:
    """Strips HTML tags and cleans up extra whitespace."""
    if not raw_html:
        return "No description available."
    clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
    return " ".join(clean_text.split())


def _evaluate_job(title: str, description: str, visa: bool, relocation: bool) -> tuple[bool, bool, int, int]:
    """
    Evaluates trade eligibility, CV match percentage, and API score.
    Returns: (is_valid_trade, cv_match, cv_match_pct, api_score)
    """
    text = f"{title} {description}".lower()

    # Hard Exclusions: Filter non-trade positions
    if any(ex in text for ex in EXCLUDED_KEYWORDS):
        return False, False, 0, 0

    # Trade Keyword Hits
    trade_hits = sum(1 for kw in SKILLED_TRADE_KEYWORDS if kw in text)
    if trade_hits == 0:
        return False, False, 0, 0

    # Score Calculations
    cv_match_pct = min(100, 40 + (trade_hits * 20))
    cv_match = cv_match_pct >= 60
    api_score = min(100, cv_match_pct + (10 if visa else 0) + (10 if relocation else 0))

    return True, cv_match, cv_match_pct, api_score


def execute_source_adapter(db: Session, source: dict) -> list:
    """
    Authoritative processing engine that ingests, cleans, evaluates, and stores jobs.
    """
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
            
            # Step 1: HTML cleanup
            clean_desc = _clean_html(raw_desc)
            
            tags = [str(t).lower() for t in raw_job.get("tags", [])]
            combined_text = f"{title.lower()} {clean_desc.lower()} {' '.join(tags)}"

            # Step 2: Benefit detection (Defaults strictly to False)
            visa_sponsored = any(p in combined_text for p in ["visa sponsorship", "visa sponsor", "visa support"])
            work_permit = any(p in combined_text for p in ["work permit", "work permit support"])
            relocation = any(p in combined_text for p in ["relocation", "relocation package", "relocation assistance"])

            # Step 3: Trade filtering & CV scoring
            is_valid_trade, cv_match, cv_match_pct, api_score = _evaluate_job(
                title, clean_desc, visa_sponsored, relocation
            )

            # Step 4: Store Job (Only valid trade jobs pass through)
            if not is_valid_trade:
                continue

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
                    cv_match=cv_match,
                    cv_match_pct=cv_match_pct,
                    api_score=api_score,
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
            logger.info(f"Source {source_name}: {len(new_inserted_jobs)} trade jobs stored successfully.")
        except Exception as commit_err:
            logger.error(f"Database commit failed: {commit_err}")
            db.rollback()
            return []
            
    return new_inserted_jobs
