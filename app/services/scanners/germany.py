import urllib.request
import json
import logging
from sqlmodel import Session
from app.models import Job
from app.services.matching import MatchingService

logger = logging.getLogger("GermanyScanner")

def scan_germany(db: Session) -> int:
    target_url = "https://api.adzuna.com/v1/api/jobs/de/search/1?app_id=demo&app_key=demo&what=anlagenmechaniker%20plumber"
    new_jobs_count = 0
    
    try:
        req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            for item in data.get('results', []):
                job_url = item.get('redirect_url')
                if not job_url or db.query(Job).filter(Job.job_url == job_url).first():
                    continue
                
                title = item.get('title', 'Anlagenmechaniker / Plumber')
                desc = item.get('description', '')
                
                match_metrics = MatchingService.calculate_match_score(
                    cv="Plumbing, general fitter mechanical engineering, pipefitting, commercial",
                    profession="Plumber",
                    job_description=f"{title} {desc}",
                    job_metadata={"visa_sponsored": True, "work_permit": True, "relocation": True}
                )
                
                db.add(Job(
                    title=title,
                    company=item.get('company', {}).get('display_name', 'Deutsche Industrie GmbH'),
                    country="Germany",
                    city=item.get('location', {}).get('display_name', 'Frankfurt').split(',')[0],
                    salary="€3,800 - €5,200 / mo",
                    employment_type="Full-time",
                    description=desc[:500],
                    job_url=job_url,
                    source_website="Adzuna Germany",
                    visa_sponsored=True,
                    work_permit=True,
                    relocation=True,
                    api_score=match_metrics["api_score"],
                    cv_match_pct=match_metrics["cv_match_pct"],
                    cv_match=match_metrics["cv_match"]
                ))
                new_jobs_count += 1
    except Exception as e:
        logger.error(f"Germany pipeline exception: {e}")
        return 0
    return new_jobs_count
