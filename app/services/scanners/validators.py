import time
import logging
from app.services.scanners.source_registry import QUARANTINE_DURATION_SECONDS, MAX_ALLOWED_FAILURES
from app.services.scanners.adapters import EuresAdapter, CanadaBulkAdapter

logger = logging.getLogger("SourceValidator")

def validate_endpoint(source_config: dict) -> bool:
    current_time = time.time()
    if source_config["current_status"] == "QUARANTINED":
        if current_time < source_config["quarantine_until"]: return False
        source_config["current_status"] = "UNVERIFIED"
        source_config["failure_count"] = 0
            
    strategy = source_config["ingestion_type"]
    adapter = EuresAdapter() if strategy == "LIVE_API" else CanadaBulkAdapter() if strategy == "BULK_DATASET" else None
    if not adapter: return False

    if adapter.validate(source_config):
        source_config["current_status"] = "HEALTHY"
        source_config["failure_count"] = 0
        return True
    else:
        source_config["failure_count"] += 1
        source_config["last_failure_time"] = current_time
        if source_config["failure_count"] >= MAX_ALLOWED_FAILURES:
            source_config["current_status"] = "QUARANTINED"
            source_config["quarantine_until"] = current_time + QUARANTINE_DURATION_SECONDS
        else:
            source_config["current_status"] = "FAILED"
        return False
