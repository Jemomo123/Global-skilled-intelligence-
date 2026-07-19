import logging

logger = logging.getLogger("SourceRegistry")

# Authoritative global dictionary mapped directly by the API health endpoint
SOURCE_REGISTRY = {
    "eures": {
        "name": "EURES API Engine",
        "url": "https://ec.europa.eu/eures/eures-apps/services/v2/jobVacancies",
        "active": True
    }
}

def get_active_sources() -> list:
    """
    Returns a structured list of running sources for the scanner core pipeline.
    """
    return [source for source in SOURCE_REGISTRY.values() if source.get("active", True)]
