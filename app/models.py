# app/models.py
"""
SQLModel Schema Definitions.
"""

from typing import Optional
from sqlmodel import SQLModel, Field


class Job(SQLModel, table=True):
    __tablename__ = "job"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    company: str = Field(index=True)
    country: str = Field(default="International", index=True)
    location: Optional[str] = Field(default="Remote / Onsite")
    description: Optional[str] = Field(default="")
    salary: Optional[str] = Field(default="N/A")
    employment_type: Optional[str] = Field(default="Full-time")

    # Perk Flags
    visa_sponsored: bool = Field(default=False)
    work_permit: bool = Field(default=False)
    relocation: bool = Field(default=False)

    # Scoring & Tracking
    cv_match: bool = Field(default=False, index=True)
    cv_match_pct: int = Field(default=0)
    api_score: int = Field(default=0)
    job_url: str = Field(default="#", unique=True, index=True)
    source: Optional[str] = Field(default="Unknown", index=True)
    created_at: Optional[str] = Field(default=None)
