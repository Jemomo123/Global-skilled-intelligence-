from typing import List
from app.services.discovery.base import BaseConnector
from app.schemas import RawDiscoveredJob

class MockAPIConnector(BaseConnector):
    @property
    def name(self) -> str:
        return "mock_api"

    @property
    def source_type(self) -> str:
        return "api"

    def fetch_jobs(self) -> List[RawDiscoveredJob]:
        # This provides sample data to verify your engine runs perfectly
        return [
            RawDiscoveredJob(
                title="Red Seal Plumber",
                company="Global Skilled Industries",
                location="Toronto, ON",
                source_type="api",
                source_url="https://example.com/jobs/1",
                raw_payload={"job_id": 1, "salary_rate": "45.00"},
                raw_description="Looking for an experienced Journeyman Plumber for commercial projects.",
                currency="CAD",
                salary_min=85000.0,
                salary_max=95000.0,
                visa_sponsored="Yes",
                relocation_offered="Yes",
                remote_friendly="No",
                contract_type="Full-time"
            )
        ]
