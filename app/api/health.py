from fastapi import APIRouter
import time
from app.services.scanners.source_registry import SOURCE_REGISTRY
from app.services.scanners.adapters import EuresAdapter, CanadaBulkAdapter

router = APIRouter()

@router.get("/api/health")
def get_system_health_matrix():
    health_reports = []
    for country, sources in SOURCE_REGISTRY.items():
        for src in sources:
            adapter = EuresAdapter() if src["ingestion_type"] == "LIVE_API" else CanadaBulkAdapter()
            report = adapter.health(src)
            report.update({"country": country, "endpoint": src["endpoint"], "quarantined": src["current_status"] == "QUARANTINED", "quarantine_remaining_seconds": max(0, int(src["quarantine_until"] - time.time()))})
            health_reports.append(report)
    return {"status": "operational", "timestamp": time.time(), "registry_health_matrix": health_reports}
