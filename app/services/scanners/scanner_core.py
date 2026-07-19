
import logging
from sqlmodel import Session
# Relative imports look directly inside the current folder path
from .source_registry import get_active_sources
from .adapters import execute_source_adapter

logger = logging.getLogger("ScannerCore")

def run_global_scanner(db: Session) -> int:
    """
    Production entry point called by the scheduler.
    Iterates through registered sources and processes vacancies.
    """
    logger.info("Starting production global scanning sequence...")
    active_sources = get_active_sources()
    total_new_jobs = 0
    
    for source in active_sources:
        try:
            logger.info(f"Processing source: {source['name']} ({source['country']})")
            new_jobs = execute_source_adapter(db, source)
            total_new_jobs += len(new_jobs) if new_jobs else 0
        except Exception as e:
            logger.error(f"Error executing source {source['name']}: {e}")
            continue
            
    logger.info(f"Global scanning sequence finished. Total jobs added: {total_new_jobs}")
    return total_new_jobs
  
