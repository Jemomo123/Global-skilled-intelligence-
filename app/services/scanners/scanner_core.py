import logging
from sqlmodel import Session
# Relative imports look directly inside the current folder path
from .source_registry import get_active_sources
from .adapters import execute_source_adapter

logger = logging.getLogger("ScannerCore")

def run_global_scanner(db: Session) -> int:
    """
    Production entry point called by the scheduler.
    Iterates through registered sources and processes vacancies with safety fallbacks.
    """
    logger.info("Starting production global scanning sequence...")
    active_sources = get_active_sources()
    total_new_jobs = 0
    
    for source in active_sources:
        try:
            # Defensive step: print exact structure to logs if things misbehave
            source_name = source.get('name', 'Unknown Source')
            
            # Safe parsing mapping to prevent KeyError: 'country'
            source_country = source.get('country') or source.get('country_code') or source.get('countries') or 'International'
            
            logger.info(f"Processing source: {source_name} ({source_country})")
            
            # Inject the processed country name safely back into the object for the adapter
            source['country'] = source_country
            
            new_jobs = execute_source_adapter(db, source)
            total_new_jobs += len(new_jobs) if new_jobs else 0
            
        except Exception as e:
            # This guarantees that a single broken key won't crash the entire background loop
            logger.error(f"Error executing source configuration matrix lookup: {e}")
            continue
            
    logger.info(f"Global scanning sequence finished. Total jobs added: {total_new_jobs}")
    return total_new_jobs
