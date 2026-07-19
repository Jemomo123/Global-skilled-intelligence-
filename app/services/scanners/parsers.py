from app.services.scanners.adapters import EuresAdapter, CanadaBulkAdapter

def execute_parse(source_config: dict, raw_payload: any) -> list:
    strategy = source_config["ingestion_type"]
    adapter = EuresAdapter() if strategy == "LIVE_API" else CanadaBulkAdapter() if strategy == "BULK_DATASET" else None
    if not adapter: return []
    parsed_jobs = adapter.parse(raw_payload)
    source_config["total_records_retrieved"] += len(parsed_jobs)
    return parsed_jobs
