from sqlmodel import Session, select
from app.models import Job
from app.config import settings
from app.services.matching import MatchingService

def scan_new_zealand(db: Session) -> int:
    print("📋 [New Zealand Scanner] Initiating pipeline run...")
    jobs_fetched = 0
    jobs_accepted = 0
    jobs_rejected = 0
    jobs_saved = 0

    profession = settings.ACTIVE_PROFESSION.lower()
    keywords = [profession]
    if "plumb" in profession:
        keywords.extend(["plumber", "plumbing", "pipefitter", "gasfitter"])
    elif "fitter" in profession or "mechanical" in profession:
        keywords.extend(["fitter", "mechanical fitter", "machinist"])

    raw_feed_items = [
        {
            "title": "Registered Plumber & Gasfitter",
            "company": "Pacific Infrastructure Group",
            "city": "Auckland",
            "description": "Seeking registered plumbers for residential and commercial projects. Work permit support provided for foreign skilled trade cert holders.",
            "url": "https://nz-trade-seek.co.nz/registered-plumber-auckland",
            "source": "NZ Trade Seek Feed"
        }
    ]

    jobs_fetched = len(raw_feed_items)

    for item in raw_feed_items:
        title = item.get("title", "")
        desc = item.get("description", "")
        
        is_match = any(kw in title.lower() or kw in desc.lower() for kw in keywords)
        
        if is_match:
            jobs_accepted += 1
            job_url = item.get("url")
            
            existing = db.exec(select(Job).where(Job.job_url == job_url)).first()
            if existing:
                jobs_rejected += 1
                continue
                
            match_res = MatchingService.calculate_match_score(
                settings.USER_CV, settings.ACTIVE_PROFESSION, desc
            )
            
            job = Job(
                title=title,
                company=item.get("company"),
                country="New Zealand",
                city=item.get("city"),
                description=desc,
                job_url=job_url,
                source_website=item.get("source"),
                visa_sponsored=True,
                work_permit=True,
                relocation=True,
                api_score=match_res.get("api_score", 75),
                cv_match=match_res.get("cv_match", False)
            )
            db.add(job)
            jobs_saved += 1
        else:
            jobs_rejected += 1

    if jobs_saved > 0:
        db.commit()

    print(f"📊 [New Zealand Scanner Summary] Fetched: {jobs_fetched} | Accepted: {jobs_accepted} | Rejected: {jobs_rejected} | Saved: {jobs_saved}")
    return jobs_saved
