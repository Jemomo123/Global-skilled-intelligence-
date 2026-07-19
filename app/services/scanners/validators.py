import logging

logger = logging.getLogger("ScannerValidators")

# Define production fallback constraints locally to eliminate broken imports
QUARANTINE_DURATION_SECONDS = 86400
MAX_ALLOWED_FAILURES = 3

def validate_job_payload(job_data: dict) -> bool:
    """
    Safely validates incoming job vacancy structures.
    Self-contained implementation ensuring an error-free startup chain.
    """
    if not job_data or not isinstance(job_data, dict):
        return False
        
    # Basic structural check to verify it contains readable content
    try:
        title = job_data.get("title") or job_data.get("positionTitle")
        if not title:
            return False
            
        return True
    except Exception as e:
        logger.error(f"Validator structural check failed: {e}")
        return False
