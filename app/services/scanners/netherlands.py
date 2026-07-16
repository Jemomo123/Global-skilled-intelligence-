from sqlmodel import Session
from app.models import Job
from app.config import settings
from app.services.matching import MatchingService

def scan_netherlands(db: Session) -> int:
    new_jobs_count = 0
    sample_feed_item = {
        "title": "Commercial Plumber",
        "company": "Delta Installation BV",
        "city": "Rotterdam",
        "description": "Commercial plumbing installation, pipeline systems, and maintenance in Rotterdam area.",
        "url": "https://netherlands-jobs-example.com/commercial-plumber-rotterdam",
        "source": "Werk NL Feed"
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
                country="Netherlands",
                city=sample_feed_item["city"],
                description=sample_feed_item["description"],
                job_url=sample_feed_item["url"],
                source_website=sample_feed_item["source"],
                visa_sponsored=True,
                work_permit=True,
                relocation=True,
                api_score=match_res["api_score"],
                cv_match=match_res["cv_match"]
            )
            db.add(job)
            db.commit()
            new_jobs_count += 1
    return new_jobs_count
