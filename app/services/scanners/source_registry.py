def get_active_sources():
    """
    Returns the authoritative list of active production sources.
    Uses the official live EURES API endpoints instead of obsolete RSS.
    """
    return [
        {
            "id": "eures_de_plumber",
            "name": "EURES Germany Plumber Portal",
            "country": "Germany",
            "url": "https://europa.eu/eures/api/jv-searchengine/public/jv-search/search",
            "payload": {
                "keywords": ["plumber"],
                "countries": ["DE"],
                "positionOpenings": 10
            }
        },
        {
            "id": "eures_nl_plumber",
            "name": "EURES Netherlands Plumber Portal",
            "country": "Netherlands",
            "url": "https://europa.eu/eures/api/jv-searchengine/public/jv-search/search",
            "payload": {
                "keywords": ["plumber"],
                "countries": ["NL"],
                "positionOpenings": 10
            }
        }
    ]
