class MatchingService:
    @staticmethod
    def calculate_match_score(job_payload: dict) -> dict:
        title = job_payload.get("title", "").lower()
        desc = job_payload.get("description", "").lower()
        combined = f"{title} {desc}"
        target_trades = ["plumber", "pipefitter", "mechanical fitter", "general fitter", "industrial maintenance", "gas fitter", "construction plumbing"]
        matched_keywords = [trade for trade in target_trades if trade in combined]
        
        cv_match_pct = 0.0
        if any(trade in title for trade in target_trades): cv_match_pct = 92.0
        elif len(matched_keywords) > 0: cv_match_pct = 78.0
            
        is_matched = cv_match_pct >= 70.0
        return {"api_score": 9.0 if is_matched else 1.0, "cv_match_pct": cv_match_pct, "cv_match": is_matched}
