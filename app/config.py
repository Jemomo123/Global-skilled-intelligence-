# app/config.py
"""
Central Configuration & Keyword Dictionaries.
"""

import os


class Settings:
    # Set active profession (Can be switched dynamically later)
    ACTIVE_PROFESSION: str = os.getenv("ACTIVE_PROFESSION", "Plumbing")
    
    # SQLite Database URI
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./global_skilled.db")
    
    # Your target trades CV profile for matching logic
    USER_CV: str = """
    Certified Plumber with over 20 years of career experience in plumbing. 
    Holds an educational certificate as a general fitter in mechanical engineering.
    Specializes in commercial and industrial piping installations, construction, 
    and supervisory duties.
    """


settings = Settings()


# ================================
# CENTRALIZED IMMIGRATION KEYWORDS
# ================================

VISA_KEYWORDS = [
    "visa sponsorship",
    "visa sponsor",
    "visa support",
    "sponsorship available",
    "work visa",
    "tier 2",
    "h1b",
    "work permit provided"
]

WORK_PERMIT_KEYWORDS = [
    "work permit",
    "work permit support",
    "right to work",
    "work authorization",
    "eligible to work"
]

RELOCATION_KEYWORDS = [
    "relocation",
    "relocation package",
    "relocation assistance",
    "relocation allowance",
    "relocation support",
    "relocation provided"
]
