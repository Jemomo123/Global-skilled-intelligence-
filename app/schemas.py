from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class RawDiscoveredJob(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    source_type: str
    source_url: str
    raw_payload: Optional[Dict[str, Any]] = None
    raw_description: Optional[str] = None
    currency: Optional[str] = "USD"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    visa_sponsored: Optional[str] = "No"
    relocation_offered: Optional[str] = "No"
    remote_friendly: Optional[str] = "No"
    contract_type: Optional[str] = "Full-time"

# This is the new schema that GSWIP will output after Python processes the data
class EnrichedJob(BaseModel):
    title: str
    company: str
    location: str
    source_type: str
    source_url: str
    description: str
    
    # Python-calculated Intelligence Fields
    cv_match: bool = False
    visa_sponsored: bool = False
    work_permit_support: bool = False
    relocation_offered: bool = False
    country: str = "Unknown"
    job_score: int = 0  # Quality score out of 100
    
    
