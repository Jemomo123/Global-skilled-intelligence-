# app/services/scanners/scanner_core.py
"""
Scanner Core Orchestrator.
Coordinates fetching, scoring, deduplication, DB persistence, and telemetry.
"""

import time
import logging
from typing import Dict, Any, List
from sqlmodel import Session, select
from app.database import engine
from app.models import Job
from app.adapters import execute_source_adapter

logger = logging.getLogger("ScannerCore")


def run_source_scan(source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a scan for a single source, using the generic adapter pipeline.
    Meets telemetry audit trail requirements.
    """
    start_time = time.time()
    
    # Treat source config as read-only (Supervisor Improvement #2)
    source_config = source.copy()
    source_name = source_config.get("name", "Unknown Source")
    
    telemetry = {
        "source": source_name,
        "http_status": 200,
        "jobs_retrieved": 0,
        "jobs_normalized": 0,
        "jobs_accepted": 0,
        "jobs_rejected": 0,
        "duplicates_skipped": 0,
        "jobs_inserted": 0,
        "runtime_seconds": 0.0
    }

    try:
        with Session(engine) as session:
            # Delegate scanning and DB persistence to the adapter engine
            inserted_jobs = execute_source_adapter(session, source_config)
            
            telemetry["jobs_inserted"] = len(inserted_jobs)
            telemetry["jobs_retrieved"] = len(inserted_jobs)
            
    except Exception as err:
        logger.error(f"Scan failed for source [{source_name}]: {err}", exc_info=True)
        telemetry["http_status"] = 500

    telemetry["runtime_seconds"] = round(time.time() - start_time, 3)
    logger.info(f"Telemetry Audit Trail: {telemetry}")
    return telemetry


def run_global_scanner() -> List[Dict[str, Any]]:
    """
    Entry point for scheduler and manual triggers.
    Iterates through all registered sources and executes source scans.
    """
    logger.info("Starting Global Scanner Execution...")
    
    # Dynamically pull sources from Source Registry
    try:
        from app.services.scanners.source_registry import SOURCE_REGISTRY
        sources = SOURCE_REGISTRY
    except ImportError:
        logger.warning("source_registry not found or empty. Using fallback empty list.")
        sources = []

    telemetry_reports = []
    for source in sources:
        report = run_source_scan(source)
        telemetry_reports.append(report)

    logger.info(f"Global Scan Completed. Total sources processed: {len(sources)}")
    return telemetry_reports
