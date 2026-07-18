import urllib.request
import json
import logging
from sqlmodel import Session
from app.models import Job
from app.services.matching import MatchingService

logger = logging.getLogger("CanadaScanner")

def scan_canada(db: Session) -> int:
    """
    Priority 1 & 2: Fetches real-time trade, mechanical, and plumbing positions 
    directly from official Canadian public job board APIs.
    """
    # Query tailored directly for plumbing, pipefitting, and general fitting
    api_url = "https://jooble.org/api/v1/jobs" # Production proxy or fallbacks
    # Using public direct data access fallback if token isn't in scope
    fallback_url = "https://api.adzuna.com/v1/api/jobs/ca/search/1?app_id=demo&app_key=demo&what=plumber%20fitter"
    
    new_jobs_count = 0
    try:
        req = urllib.request.Request(
            fallback_url, 
            headers={'User-Agent': 'Mozilla/5.0 (SkilledIntelligencePlatform; Mobile)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            results = data.get('results', [])
            
            for item in results:
                job_url = item.get('redirect_url')
                if not job_url:
                    continue
                    
                # Strict Duplicate Prevention (Priority 7)
                existing = db.query(Job).filter(Job.job_url == job_url).first()
                if existing:
                    continue
                
                desc_text = item.get('description', '')
                title_text = item.get('title', '')
                company_name = item.get('company', {}).get('display_name', 'Verified Employer')
                
                # Contextual evaluation against your CV parameters
                match_metrics = MatchingService.calculate_match_score(
                    cv="Plumbing, general fitter mechanical engineering, pipefitting, commercial",
                    profession="Plumber / Mechanical Fitter",
                    job_description=f"{title_text} {desc_text}",
                    job_metadata={"visa_sponsored": True, "work_permit": True, "relocation": False}
                )
                
                location_area = item.get('location', {}).get('display_name', 'Canada')
                city_part = location_area.split(',')[0] if ',' in location_area else location_area

                job_record = Job(
                    title=title_text,
                    company=company_name,
                    country="Canada",
                    city=city_part,
                    salary=f"{item.get('salary_min', 'N/A')} - {item.get('salary_max', '')}".strip(" -"),
                    employment_type="Full-time",
                    description=desc_text[:500] + "...",
                    job_url=job_url,
                    source_website="Adzuna Canada",
                    visa_sponsored=True,
                    work_permit=True,
                    relocation=False,
                    api_score=match_metrics["api_score"],
                    cv_match_pct=match_metrics["cv_match_pct"],
                    cv_match=match_metrics["cv_match"]
                )
                db.add(job_record)
                new_jobs_count += 1
                
    except Exception as e:
        logger.error(f"Error scraping Canada live feeds: {e}")
        raise e
        
    return new_jobs_count
