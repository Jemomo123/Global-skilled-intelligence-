import time
from typing import Dict, Any, List

SOURCE_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    "Europe": [
        {
            "source_name": "EURES Live Search Portal Engine Primary",
            "priority": 1,
            "endpoint": "https://europa.eu/eures/api/jv-searchengine/public/jv-search/search",
            "method": "POST",
            "ingestion_type": "LIVE_API",
            "countries": ["DE", "NL", "HR", "PL"],
            "expected_format": "JSON",
            "current_status": "UNVERIFIED",
            "failure_count": 0,
            "quarantine_until": 0.0,
            "last_success_time": None,
            "last_failure_time": None,
            "avg_response_time": 0.0,
            "total_records_retrieved": 0,
            "total_records_matched": 0
        }
    ],
    "Canada": [
        {
            "source_name": "Open Government Canada Package Registry Primary",
            "priority": 1,
            "endpoint": "https://open.canada.ca/data/en/api/3/action/package_show?id=national-job-bank-feed",
            "method": "GET",
            "ingestion_type": "BULK_DATASET",
            "countries": ["CA"],
            "expected_format": "JSON",
            "current_status": "UNVERIFIED",
            "failure_count": 0,
            "quarantine_until": 0.0,
            "last_success_time": None,
            "last_failure_time": None,
            "avg_response_time": 0.0,
            "total_records_retrieved": 0,
            "total_records_matched": 0
        }
    ]
}

QUARANTINE_DURATION_SECONDS = 1800
MAX_ALLOWED_FAILURES = 3
