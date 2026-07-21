# app/services/scanners/germany.py
"""
Germany Job Adapter & Scanner Integration.
Fetches German job listings via production API/Sources and transforms them 
for the unified scanner pipeline.
"""

import logging
from typing import List, Dict, Any, Optional
import httpx

from app.database import Job  # ISSUE 3: Single unified Job model
from app.services.matching import calculate_job_match  # ISSUE 4: Dynamic CV scoring pipeline

logger = logging.getLogger("GermanyScanner")

# ISSUE 1: Production endpoints for Germany (Arbeitsagentur / Supported API)
GERMANY_JOB_API_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"


def fetch_germany_jobs(keywords: List[str] = None) -> List[Dict[Any, Any]]:
    """
    Fetches live German job listings dynamically from supported production endpoints.
    """
    if not keywords:
        keywords = ["Plumber", "General Fitter", "Mechanical Engineer", "Technician"]

    raw_jobs: List[Dict[Any, Any]] = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "OAuth2Token": "public"  # Standard public API token for Arbeitsagentur API
    }

    async_client = httpx.Client(timeout=10.0, headers=headers)

    for kw in keywords:
        try:
            params = {
                "was": kw,
                "wo": "Deutschland",
                "page": 1,
                "size": 20
            }
            response = async_client.get(GERMANY_JOB_API_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("stellenangebote", [])
                raw_jobs.extend(results)
            else:
                logger.warning(f"Failed to fetch Germany jobs for '{kw}'. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Error requesting Germany job API for '{kw}': {e}")

    return raw_jobs


def parse_germany_job(raw_data: Dict[Any, Any], user_profile: Optional[Dict[str, Any]] = None) -> Optional[Job]:
    """
    Transforms raw source data into a unified Job model instance.
    Extracts dynamic metadata and avoids hardcoded values.
    """
    try:
        title = raw_data.get("titel") or raw_data.get("jobTitle")
        if not title:
            return None

        # ISSUE 5: Dynamic employer extraction
        company = raw_data.get("arbeitgeber") or raw_data.get("employer", "German Employer")

        # ISSUE 6: Dynamic city/location extraction
        location_info = raw_data.get("arbeitsort", {})
        city = location_info.get("ort") if isinstance(location_info, dict) else raw_data.get("location")
        location = f"{city}, Germany" if city else "Germany (Various Locations)"

        # ISSUE 7: Dynamic salary extraction or default to "N/A"
        salary = raw_data.get("gehalt") or raw_data.get("salary") or "N/A"

        description = raw_data.get("refnr") or f"Position: {title} at {company}"
        ref_nr = raw_data.get("refnr", "")
        job_url = f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{ref_nr}" if ref_nr else raw_data.get("url", "#")

        # Perk indicators detection from title/description
        visa_sponsored = "visa" in title.lower() or "relocation" in title.lower()
        work_permit = "eu passport" in title.lower() or "work permit" in title.lower()
        relocation = "relocation" in title.lower() or "unterkunft" in title.lower()

        # ISSUE 4: Score using user profile dynamically instead of hardcoded CV text
        match_score = 0
        cv_match_flag = False
        if user_profile:
            match_score, cv_match_flag = calculate_job_match(title, description, user_profile)

        job_obj = Job(
            title=title,
            company=company,
            country="Germany",
            location=location,
            description=description,
            salary=salary,
            employment_type=raw_data.get("arbeitszeit", "Full-time"),
            visa_sponsored=visa_sponsored,
            work_permit=work_permit,
            relocation=relocation,
            cv_match=cv_match_flag,
            cv_match_pct=match_score,
            job_url=job_url,
            source="Arbeitsagentur Germany API"
        )
        return job_obj

    except Exception as e:
        logger.error(f"Error parsing Germany job item: {e}")
        return None


# ISSUE 2 & ISSUE 8: Unified processing entrypoint for scanner_core / adapters
def process_germany_jobs(db_session, user_profile: Optional[Dict[str, Any]] = None) -> List[Job]:
    """
    Main integrated pipeline function called by scanner_core / source_registry.
    Batch processes, stages jobs, and performs a single bulk database commit.
    """
    logger.info("Starting Germany Job Source Pipeline...")
    raw_listings = fetch_germany_jobs()
    parsed_jobs: List[Job] = []

    for item in raw_listings:
        job = parse_germany_job(item, user_profile=user_profile)
        if job:
            # Check for existing job to avoid duplicates
            existing = db_session.query(Job).filter(Job.job_url == job.job_url).first() if hasattr(db_session, "query") else None
            if not existing:
                db_session.add(job)  # Staging in session
                parsed_jobs.append(job)

    # ISSUE 8: Single bulk commit after processing all listings
    try:
        db_session.commit()
        logger.info(f"Germany Pipeline Completed: {len(parsed_jobs)} new jobs inserted.")
    except Exception as e:
        db_session.rollback()
        logger.error(f"Failed to commit Germany jobs to database: {e}")

    return parsed_jobs
