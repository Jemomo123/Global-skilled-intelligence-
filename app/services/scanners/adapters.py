import logging
from sqlmodel import Session
from .fetchers import execute_http_fetch
from .parsers import parse_raw_response
from .validators import validate_job_payload
from .matcher import match_job_requirements

logger = logging.getLogger("ScannerAdapters")

def execute_source_adapter(db: Session, source: dict) -> list:
    """
    Authoritative public entry point for the adapter layer.
    Orchestrates fetching, parsing, validation, and database matching.
    """
    logger.info(f"Adapter: Processing orchestration pipeline for {source['name']}")
    
    # 1. Fetch data from source URL
    raw_data = execute_http_fetch(source["url"], source.get("payload"))
    if not raw_data:
        logger.warning(f"Adapter: No data fetched for {source['name']}")
        return []
        
    # 2. Parse source data structural response
    parsed_jobs = parse_raw_response(raw_data)
    if not parsed_jobs:
        logger.warning(f"Adapter: Parsing yielded zero results for {source['name']}")
        return []
        
    # 3. Validate structures and run database matching
    valid_new_jobs = []
    for raw_job in parsed_jobs:
        if validate_job_payload(raw_job):
            processed_job = match_job_requirements(db, raw_job, source)
            if processed_job:
                valid_new_jobs.append(processed_job)
                
    logger.info(f"Adapter: Successfully processed {len(valid_new_jobs)} jobs for {source['name']}")
    return valid_new_jobs
