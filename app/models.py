# app/models.py
from typing import Optional
from sqlmodel import SQLModel, Field

class Job(SQLModel, table=True):
    __tablename__ = "job"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    company: str
    location: Optional[str] = None
    url: str
    source: Optional[str] = None
    cv_match: bool = False
