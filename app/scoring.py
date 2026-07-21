# app/scoring.py
"""
Scoring & Relevance Intelligence Engine.

This module evaluates raw job listings against target skilled trade criteria,
calculating trade relevance, CV match percentage, and overall API scores.
"""

import re
from typing import List, Dict, Any

# Initial Default Target Keyword Lists
DEFAULT_SKILLED_TRADE_KEYWORDS: List[str] = [
    "plumber", "plumbing", "pipefitter", "pipe fitter", "mechanical fitter",
    "fitter", "hvac", "welder", "welding", "electrician", "electrical",
    "construction maintenance", "industrial maintenance", "maintenance technician",
    "mechanical technician", "carpenter", "mason", "painter", "steel fixer",
    "crane operator", "heavy equipment operator", "millwright", "boilermaker", "gas fitter"
]

DEFAULT_EXCLUDED_KEYWORDS: List[str] = [
    "software", "ai engineer", "data engineer", "marketing", "sales", 
    "human resources", "hr", "finance", "commercial director", "accountant"
]


def get_trade_keywords(custom_keywords: List[str] = None) -> List[str]:
    """
    Returns configured trade keywords. Accepts custom keyword lists for dynamic expansion.
    """
    if custom_keywords:
        return custom_keywords
    return DEFAULT_SKILLED_TRADE_KEYWORDS


def get_excluded_keywords(custom_exclusions: List[str] = None) -> List[str]:
    """
    Returns configured exclusion keywords. Accepts custom exclusion lists for dynamic expansion.
    """
    if custom_exclusions:
        return custom_exclusions
    return DEFAULT_EXCLUDED_KEYWORDS


def score_job(
    title: str, 
    description: str, 
    visa: bool = False, 
    relocation: bool = False,
    custom_trades: List[str] = None,
    custom_exclusions: List[str] = None
) -> Dict[str, Any]:
    """
    Evaluates job text for trade relevance and immigration suitability.

    Args:
        title (str): Job listing title.
        description (str): Cleaned job description text.
        visa (bool): Explicit visa sponsorship availability flag.
        relocation (bool): Explicit relocation support availability flag.
        custom_trades (List[str], optional): Override list of trade keywords.
        custom_exclusions (List[str], optional): Override list of excluded keywords.

    Returns:
        Dict[str, Any]: Structured evaluation payload:
            - "cv_match" (bool): Meets minimum trade confidence threshold.
            - "cv_match_pct" (int): Scaled percentage score for trade match relevance (0-100).
            - "api_score" (int): Overall aggregated listing value incorporating perks (0-100).
    """
    text = f"{title or ''} {description or ''}".lower()

    trade_keywords = get_trade_keywords(custom_trades)
    excluded_keywords = get_excluded_keywords(custom_exclusions)

    # Hard Exclusions: Immediately reject tech/corporate roles using word boundaries
    for ex in excluded_keywords:
        if re.search(rf"\b{re.escape(ex.lower())}\b", text):
            return {
                "cv_match": False,
                "cv_match_pct": 0,
                "api_score": 0
            }

    # Trade Keyword Hits using word boundaries
    trade_hits = 0
    for kw in trade_keywords:
        if re.search(rf"\b{re.escape(kw.lower())}\b", text):
            trade_hits += 1

    if trade_hits == 0:
        return {
            "cv_match": False,
            "cv_match_pct": 0,
            "api_score": 10
        }

    # Score Calculations
    cv_match_pct = min(100, 40 + (trade_hits * 20))
    cv_match = cv_match_pct >= 60
    api_score = min(100, cv_match_pct + (10 if visa else 0) + (10 if relocation else 0))

    return {
        "cv_match": cv_match,
        "cv_match_pct": cv_match_pct,
        "api_score": api_score
    }
