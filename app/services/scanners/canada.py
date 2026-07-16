import httpx
from sqlmodel import Session
from app.models import Job
from app.config import settings
from app.services.matching import MatchingService

def scan_canada(db: Session) -> int:
    new_jobs_count = 0
    url = "https://www.arbeitnow.com/api/job-board-api"
    try:
        response = httpx.get(url, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("data", []):
                desc = item.get("description", "")
                title = item.get("title", "")
                
                # Filter dynamically based on your active trade configuration (Plumbing)
                if settings.ACTIVE_PROFESSION.lower() in title.lower() or settings.ACTIVE_PROFESSION.lower() in desc.lower():
                    job_url = item.get("url")
                    
                    # Prevent Duplicate Entry
                    existing = db.query(Job).filter(Job.job_url == job_url).first()
                    if existing:
                        continue
                        
                    match_res = MatchingService.calculate_match_score(
                        settings.USER_CV, settings.ACTIVE_PROFESSION, desc
                    )
                    
                    job = Job(
                        title=title,
                        company=item.get("company_name", "Unknown Company"),
                        country="Canada",
                        city="Toronto",
                        description=desc[:500] + "...",
                        job_url=job_url,
                        source_website="Arbeitnow Public Feed",
                        visa_sponsored=True,
                        work_permit=True,
                        relocation=True,
                        api_score=match_res["api_score"],
                        cv_match=match_res["cv_match"]
                    )
                    db.add(job)
                    new_jobs_count += 1
            db.commit()
    except Exception as e:
        print(f"Error scanning Canada: {e}")
    return new_jobs_count
