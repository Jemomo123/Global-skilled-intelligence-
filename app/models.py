from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    company: str
    country: str
    city: str
    salary: Optional[str] = "N/A"
    employment_type: Optional[str] = "Full-time"
    description: str
    job_url: str = Field(unique=True)  # Unique index prevents duplicates
    source_website: str
    date_discovered: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Sponsorship & Benefits
    visa_sponsored: bool = False
    work_permit: bool = False
    relocation: bool = False
    employer_immigration_support: bool = False
    
    # Selection metrics (Upgraded for Phase 2 & 3 Compliance)
    api_score: int = 0
    cv_match_pct: int = 0  # Stores the precise percentage match from the ATS parser
    cv_match: bool = False

class ScanHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    jobs_found: int
    errors_logged: Optional[str] = None
