import logging

logger = logging.getLogger("ScannerParsers")

def parse_raw_response(raw_data: dict) -> list:
    """
    Safely parses structural response payloads from the live endpoints.
    Isolated entry point to completely eliminate circular module dependencies.
    """
    if not raw_data:
        return []
        
    # Standardize data into a uniform iterable list for the pipeline
    try:
        # Check for EURES search engine response structure
        if "items" in raw_data:
            return raw_data["items"]
        # Fallback if raw data is already an formatted list
        if isinstance(raw_data, list):
            return raw_data
            
        return []
    except Exception as e:
        logger.error(f"Parser encountered unexpected structural error: {e}")
        return []
