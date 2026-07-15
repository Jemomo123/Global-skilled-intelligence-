from typing import List
from app.schemas import RawDiscoveredJob
from app.services.discovery.base import BaseConnector
from app.services.discovery.connectors import MockAPIConnector

class DiscoveryEngine:
    def __init__(self):
        # Automatically register your connectors here
        self.connectors: List[BaseConnector] = [
            MockAPIConnector()
        ]

    def run_all(self) -> List[RawDiscoveredJob]:
        all_jobs: List[RawDiscoveredJob] = []
        for connector in self.connectors:
            try:
                jobs = connector.fetch_jobs()
                all_jobs.extend(jobs)
            except Exception as e:
                # Keep going even if one connector fails
                print(f"Error running connector {connector.name}: {str(e)}")
        return all_jobs
