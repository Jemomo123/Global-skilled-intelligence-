from typing import List, Set
from app.schemas import RawDiscoveredJob, EnrichedJob
from app.services.discovery.base import BaseConnector
from app.services.discovery.connectors import MockAPIConnector

class DiscoveryEngine:
    def __init__(self):
        self.connectors: List[BaseConnector] = [
            MockAPIConnector()
        ]

    def run_all(self) -> List[EnrichedJob]:
        raw_jobs: List[RawDiscoveredJob] = []
        for connector in self.connectors:
            try:
                jobs = connector.fetch_jobs()
                raw_jobs.extend(jobs)
            except Exception as e:
                print(f"Error running connector {connector.name}: {str(e)}")
        
        return self.process_and_enrich_jobs(raw_jobs)

    def process_and_enrich_jobs(self, raw_jobs: List[RawDiscoveredJob]) -> List[EnrichedJob]:
        enriched_jobs: List[EnrichedJob] = []
        seen_urls: Set[str] = set()

        for raw in raw_jobs:
            # 1. Duplicate Removal (By URL)
            if raw.source_url in seen_urls:
                continue
            seen_urls.add(raw.source_url)

            # 2. Setup Base Text for Matching
            desc_text = (raw.raw_description or "").lower()
            title_text = raw.title.lower()
            combined_text = f"{title_text} {desc_text}"

            # 3. CV Match Detection (Plumbing & Mechanical Backgrounds)
            cv_match = any(term in combined_text for term in ["plumb", "fitter", "mechanical"])

            # 4. Visa & Work Permit Detection
            visa_sponsored = raw.visa_sponsored.lower() == "yes" or "visa sponsor" in desc_text
            work_permit_support = visa_sponsored or "work permit" in desc_text

            # 5. Relocation Detection
            relocation_offered = raw.relocation_offered.lower() == "yes" or "relocation" in desc_text

            # 6. Country Classification
            country = "Unknown"
            if raw.location:
                parts = raw.location.split(",")
                country = parts[-1].strip()

            # 7. Job Scoring (Institutional grading system)
            score = 0
            if cv_match:
                score += 40
            if visa_sponsored:
                score += 25
            if relocation_offered:
                score += 20
            if work_permit_support:
                score += 15
            # Cap the score at 100
            score = min(score, 100)

            # Assemble the Enriched Record
            enriched_jobs.append(
                EnrichedJob(
                    title=raw.title,
                    company=raw.company,
                    location=raw.location or "Remote",
                    source_type=raw.source_type,
                    source_url=raw.source_url,
                    description=raw.raw_description or "",
                    cv_match=cv_match,
                    visa_sponsored=visa_sponsored,
                    work_permit_support=work_permit_support,
                    relocation_offered=relocation_offered,
                    country=country,
                    job_score=score
                )
            )

        # Sort jobs by highest score first
        return sorted(enriched_jobs, key=lambda x: x.job_score, reverse=True)
