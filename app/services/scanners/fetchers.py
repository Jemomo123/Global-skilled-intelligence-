import time
from typing import Any
from app.services.scanners.adapters import EuresAdapter, CanadaBulkAdapter

def execute_fetch(source_config: dict) -> Any:
    strategy = source_config["ingestion_type"]
    if strategy == "LIVE_API": adapter = EuresAdapter()
    elif strategy == "BULK_DATASET": adapter = CanadaBulkAdapter()
    else: raise ValueError(f"Unsupported framework strategy: {strategy}")

    start_time = time.time()
    try:
        data = adapter.fetch(source_config)
        latency = time.time() - start_time
        source_config["last_success_time"] = time.time()
        source_config["avg_response_time"] = latency if source_config["avg_response_time"] == 0.0 else (source_config["avg_response_time"] * 0.7) + (latency * 0.3)
        return data
    except Exception as ex:
        source_config["last_failure_time"] = time.time()
        raise ex
