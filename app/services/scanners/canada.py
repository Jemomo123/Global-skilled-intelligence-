import httpx
from sqlmodel import Session, select
from app.models import Job
from app.config import settings
from app.services.matching import MatchingService

def scan_canada(db: Session) -> int:
    new_jobs_count = 0
    url = "https://www.arbeitnow.com/api/job-board-api"
    
    # Establish flexible keyword stems based on active trades to prevent string mismatches
    profession = settings.ACTIVE_PROFESSION.lower()
    keywords = [profession]
    
    if "plumb" in profession:
        keywords.extend(["plumber", "plumbing", "pipefitter", "gasfitter"])
    elif "fitter" in profession or "mechanical" in profession:
        keywords.extend(["fitter", "mechanical fitter", "machinist", "millwright"])

    try:
        response = httpx.get(url, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("data", []):
                title = item.get("title", "") or ""
                desc = item.get("description", "") or ""
                
                title_lower = title.lower()
                desc_lower = desc.lower()
                
                # Verify if any of our expanded trade keywords hit the target fields
                is_match = any(kw in title_lower or kw in desc_lower for kw in keywords)
                
                if is_match:
                    job_url = item.get("url")
                    if not job_url:
                        continue
                    
                    # Prevent Duplicate Entry using strict SQLModel standard syntax
                    existing = db.exec(select(Job).where(Job.job_url == job_url)).first()
                    if existing:
                        continue
                        
                    match_res = MatchingService.calculate_match_score(
                        settings.USER_CV, settings.ACTIVE_PROFESSION, desc
                    )
                    
                    job = Job(
                        title=title,
                        company=item.get("company_name", "Unknown Company"),
                        country="Canada",
                        city=item.get("location", "Toronto"),
                        description=desc[:500] + "...",
                        job_url=job_url,
                        source_website="Arbeitnow Public Feed",
                        visa_sponsored=True,
                        work_permit=True,
                        relocation=True,
                        api_score=match_res.get("api_score", 70),
                        cv_match=match_res.get("cv_match", False)
                    )
                    db.add(job)
                    new_jobs_count += 1
            
            if new_jobs_count > 0:
                db.commit()
                
    except Exception as e:
        print(f"Error scanning Canada: {e}")
        
    return new_jobs_count
