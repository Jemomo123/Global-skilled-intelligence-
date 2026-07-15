from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class RawDiscoveredJob(BaseModel):
    title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    location: Optional[str] = None
    source_type: str = Field(..., pattern="^(api|html|js)$")
    source_url: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None
    raw_description: Optional[str] = None
    currency: Optional[str] = "USD"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    visa_sponsored: Optional[str] = "Unknown"
    relocation_offered: Optional[str] = "Unknown"
    remote_friendly: Optional[str] = "Unknown"
    contract_type: Optional[str] = "Unknown"
