from sqlmodel import Session, select
from app.models import Job
from app.config import settings
from app.services.matching import MatchingService

def scan_germany(db: Session) -> int:
    print("📋 [Germany Scanner] Initiating pipeline run...")
    jobs_fetched = 0
    jobs_accepted = 0
    jobs_rejected = 0
    jobs_saved = 0

    profession = settings.ACTIVE_PROFESSION.lower()
    keywords = [profession]
    if "plumb" in profession:
        keywords.extend(["plumber", "plumbing", "pipefitter"])
    elif "fitter" in profession or "mechanical" in profession:
        keywords.extend(["fitter", "mechanical fitter", "machinist", "millwright"])

    raw_feed_items = [
        {
            "title": "Sanitary and Heating Plumber",
            "company": "Müller Haustechnik GmbH",
            "city": "Munich",
            "description": "Installation of heating systems and sanitaries. Pipefitting and mechanical engineering certifications are highly valued.",
            "url": "https://germany-arbeit-agentur.de/sanitary-plumber-munich",
            "source": "Arbeit Agentur Feed"
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
                country="Germany",
                city=item.get("city"),
                description=desc,
                job_url=job_url,
                source_website=item.get("source"),
                visa_sponsored=False,
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

    print(f"📊 [Germany Scanner Summary] Fetched: {jobs_fetched} | Accepted: {jobs_accepted} | Rejected: {jobs_rejected} | Saved: {jobs_saved}")
    return jobs_saved
