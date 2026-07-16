from sqlmodel import Session
from app.models import Job
from app.config import settings
from app.services.matching import MatchingService

def scan_croatia(db: Session) -> int:
    new_jobs_count = 0
    sample_feed_item = {
        "title": "Lead Plumber - Shipyard Maintenance",
        "company": "Adria Marine Fitter Ltd",
        "city": "Rijeka",
        "description": "Seeking expert general fitter and plumber with experience in commercial pipefitting installations.",
        "url": "https://croatia-jobs-example.com/plumber-rijeka-123",
        "source": "Croatia Trade Portal"
    }
    
    if settings.ACTIVE_PROFESSION.lower() in sample_feed_item["title"].lower():
        existing = db.query(Job).filter(Job.job_url == sample_feed_item["url"]).first()
        if not existing:
            match_res = MatchingService.calculate_match_score(
                settings.USER_CV, settings.ACTIVE_PROFESSION, sample_feed_item["description"]
            )
            job = Job(
                title=sample_feed_item["title"],
                company=sample_feed_item["company"],
                country="Croatia",
                city=sample_feed_item["city"],
                description=sample_feed_item["description"],
                job_url=sample_feed_item["url"],
                source_website=sample_feed_item["source"],
                visa_sponsored=True,
                work_permit=True,
                relocation=False,
                api_score=match_res["api_score"],
                cv_match=match_res["cv_match"]
            )
            db.add(job)
            db.commit()
            new_jobs_count += 1
    return new_jobs_count
