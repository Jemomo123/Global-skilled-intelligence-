import re

class MatchingService:
    @staticmethod
    def calculate_match_score(cv: str, profession: str, job_description: str) -> dict:
        """
        Calculates a compatibility score (0-100) and CV match status 
        by comparing job description criteria against your CV.
        """
        score = 0
        cv_lower = cv.lower()
        desc_lower = job_description.lower()
        prof_lower = profession.lower()

        # 1. Active profession check (Plumbing)
        if prof_lower in desc_lower:
            score += 30

        # 2. Key trade elements matching (highly weighted)
        keywords = {
            "pipefitting": 10,
            "mechanical installation": 10,
            "construction": 10,
            "commercial": 10,
            "industrial": 10,
            "supervision": 10,
            "fitter": 5,
            "red seal": 5
        }

        for keyword, weight in keywords.items():
            if keyword in desc_lower and keyword in cv_lower:
                score += weight

        final_score = min(score, 100)
        cv_match = final_score >= 60

        return {
            "api_score": final_score,
            "cv_match": cv_match
        }
