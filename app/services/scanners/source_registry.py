# Standardized global definition to prevent health endpoint import crashes
SOURCE_REGISTRY = [
    {
        "name": "Arbeitnow API Engine",
        "country": "Germany",
        "country_code": "DE",
        "api_url": "https://www.arbeitnow.com/api/job-board-api",
        "is_active": True
    }
]

def get_active_sources() -> list:
    """
    Returns the collection of active, working production data sources.
    Replaces the dead EURES v2 API with a reliable live public job discovery endpoint.
    """
    return [s for s in SOURCE_REGISTRY if s.get("is_active", True)]
