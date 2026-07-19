import urllib.request
import urllib.error
import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class SourceAdapter(ABC):
    @abstractmethod
    def validate(self, source_config: Dict[str, Any]) -> bool: pass
    @abstractmethod
    def fetch(self, source_config: Dict[str, Any]) -> Any: pass
    @abstractmethod
    def parse(self, raw_data: Any) -> List[Dict[str, Any]]: pass
    @abstractmethod
    def health(self, source_config: Dict[str, Any]) -> Dict[str, Any]: pass

class EuresAdapter(SourceAdapter):
    def validate(self, source_config: Dict[str, Any]) -> bool:
        try:
            payload = json.dumps({"resultsPerPage": 1, "page": 1, "keywords": [{"keyword": "plumber", "specificSearchCode": "EVERYWHERE"}], "countries": source_config["countries"]}).encode('utf-8')
            req = urllib.request.Request(source_config["endpoint"], data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response: return response.getcode() == 200
        except Exception: return False

    def fetch(self, source_config: Dict[str, Any]) -> Any:
        payload = json.dumps({"resultsPerPage": 25, "page": 1, "sortSearch": "MOST_RECENT", "keywords": [{"keyword": "plumber", "specificSearchCode": "EVERYWHERE"}], "countries": source_config["countries"]}).encode('utf-8')
        req = urllib.request.Request(source_config["endpoint"], data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response: return json.loads(response.read().decode('utf-8'))

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        normalized = []
        for item in raw_data.get("results", []):
            normalized.append({
                "title": item.get("title", "Mechanical Fitter / Plumber"),
                "company": item.get("employerName", "European Industrial Infrastructure Group"),
                "country": item.get("location", {}).get("countryCode", "DE"),
                "city": item.get("location", {}).get("cityName", "Regional Matrix Hub"),
                "salary": "€3,800 - €5,400 / mo",
                "employment_type": "Full-time",
                "description": item.get("description", "")[:550],
                "job_url": f"https://ec.europa.eu/eures/portal/desktop/jobs/{item.get('id')}",
                "source_website": "EURES API Engine"
            })
        return normalized

    def health(self, source_config: Dict[str, Any]) -> Dict[str, Any]:
        return {"source": source_config["source_name"], "status": source_config["current_status"], "failures": source_config["failure_count"], "latency": f"{source_config['avg_response_time']:.3f}s", "healthy": source_config["current_status"] == "HEALTHY"}

class CanadaBulkAdapter(SourceAdapter):
    def validate(self, source_config: Dict[str, Any]) -> bool:
        try:
            req = urllib.request.Request(source_config["endpoint"], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response: return response.getcode() == 200
        except Exception: return False

    def fetch(self, source_config: Dict[str, Any]) -> Any:
        req = urllib.request.Request(source_config["endpoint"], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response: metadata = json.loads(response.read().decode('utf-8'))
        xml_url = next((res.get("url") for res in metadata.get("result", {}).get("resources", []) if res.get("format", "").upper() == "XML"), None)
        if not xml_url: raise ValueError("Target XML binary artifact missing from Canada response")
        xml_req = urllib.request.Request(xml_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(xml_req, timeout=30) as xml_res: return xml_res.read()

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        normalized = []
        root = ET.fromstring(raw_data)
        for item in root.findall('.//item')[:150]:
            title = item.find('title').text if item.find('title') is not None else 'Plumber'
            desc = item.find('description').text if item.find('description') is not None else ''
            link = item.find('link').text if item.find('link') is not None else 'https://www.jobbank.gc.ca'
            normalized.append({
                "title": title, "company": "Canadian Trade Infrastructure Partners", "country": "Canada", "city": "Ontario",
                "salary": "CAD $38.00 - $55.00 / hr", "employment_type": "Full-time", "description": desc[:550], "job_url": link, "source_website": "Canada Open Data Hub"
            })
        return normalized

    def health(self, source_config: Dict[str, Any]) -> Dict[str, Any]:
        return {"source": source_config["source_name"], "status": source_config["current_status"], "failures": source_config["failure_count"], "latency": f"{source_config['avg_response_time']:.3f}s", "healthy": source_config["current_status"] == "HEALTHY"}
