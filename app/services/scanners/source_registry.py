def get_active_sources() -> list:
    """
    Returns the collection of active, working production data sources.
    Replaces the dead EURES v2 API with a reliable live public job discovery endpoint.
    """
    return [
        {
            "name": "Arbeitnow API Engine",
            "country": "Germany",
            "country_code": "DE",
            "api_url": "https://www.arbeitnow.com/api/job-board-api",
            "is_active": True
        }
    ]
