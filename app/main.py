from fastapi import FastAPI
from typing import List
from app.schemas import RawDiscoveredJob
from app.services.discovery.engine import DiscoveryEngine

app = FastAPI(title="Global Skilled Intelligence API")
discovery_engine = DiscoveryEngine()

@app.get("/")
def read_root():
    return {"message": "Global Skilled Intelligence API is running successfully!"}

@app.get("/jobs/discover", response_model=List[RawDiscoveredJob])
def discover_jobs():
    """Runs all registered discovery connectors and returns discovered jobs."""
    jobs = discovery_engine.run_all()
    return jobs
