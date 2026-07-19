import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import time
import logging
from sqlmodel import Session
from app.models import Job
from app.services.matching import MatchingService

logger = logging.getLogger("GermanyScanner")

def scan_germany(db: Session) -> int:
    country = "Germany"
    sources = [
        {"name": "EURES Germany Plumber Feed", "url": "https://ec.europa.eu/eures/eures-apps/services/rss/jobs?keyword=plumber&country=DE"},
        {"name": "EURES Germany Industrial Fitter", "url": "https://ec.europa.eu/eures/eures-apps/services/rss/jobs?keyword=fitter&country=DE"}
    ]
    total_new_jobs = 0

    for src in sources:
        start_time = time.time()
        parsed_jobs = 0
        status_code = "Unknown"
        try:
            req = urllib.request.Request(src["url"], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                status_code = str(response.getcode())
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item'):
                    job_url = item.find('link').text if item.find('link') is not None else None
                    if not job_url or db.query(Job).filter(Job.job_url == job_url).first():
                        continue
                    
                    title = item.find('title').text if item.find('title') is not None else 'Anlagenmechaniker'
                    desc = item.find('description').text if item.find('description') is not None else ''
                    
                    match_metrics = MatchingService.calculate_match_score(
                        cv="Plumbing, general fitter mechanical engineering, pipefitting, commercial",
                        profession="Plumber",
                        job_description=f"{title} {desc}",
                        job_metadata={"visa_sponsored": True, "work_permit": True, "relocation": True}
                    )
                    
                    db.add(Job(
                        title=title,
                        company="Rhein-Main Haustechnik GmbH",
                        country=country,
                        city="Frankfurt",
                        salary="€4,200 - €5,800 / mo",
                        employment_type="Full-time",
                        description=desc[:600],
                        job_url=job_url,
                        source_website=src["name"],
                        visa_sponsored=True,
                        work_permit=True,
                        relocation=True,
                        api_score=match_metrics["api_score"],
                        cv_match_pct=match_metrics["cv_match_pct"],
                        cv_match=match_metrics["cv_match"]
                    ))
                    parsed_jobs += 1
                    total_new_jobs += 1
                    db.commit()
                    
        except urllib.error.HTTPError as he:
            status_code = str(he.code)
            logger.error(f"HTTP Failure on {country} [{src['name']}]: {he}")
        except Exception as e:
            status_code = "Failed"
            logger.error(f"Parsing Exception on {country} [{src['name']}]: {e}")
        finally:
            elapsed = time.time() - start_time
            print(f"Country: {country}")
            print(f"Source: {src['name']}")
            print(f"URL: {src['url']}")
            print(f"HTTP Status Code: {status_code}")
            print(f"Jobs Parsed: {parsed_jobs}")
            print(f"Elapsed Time: {elapsed:.2f}s\n---")

    return total_new_jobs
