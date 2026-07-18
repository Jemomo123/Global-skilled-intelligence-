import re

class MatchingService:
    @staticmethod
    def calculate_match_score(cv: str, profession: str, job_description: str, job_metadata: dict = None) -> dict:
        """
        Calculates an advanced 0-100 weighted compatibility score and an ATS-aware CV Match percentage
        based on active trade domain alignment, structural parameters, and compliance pathways.
        """
        if not job_metadata:
            job_metadata = {}

        cv_lower = cv.lower()
        desc_lower = job_description.lower()
        prof_lower = profession.lower()
        
        # Initialize sub-category scores
        trade_score = 0      # Max 30
        exp_score = 0        # Max 25
        domain_score = 0     # Max 20
        compliance_score = 0 # Max 25

        # ==================================================
        # 1. TRADE RELEVANCE & CERTIFICATIONS (Max 30)
        # ==================================================
        # Broaden keyword stems to accurately identify matching specializations
        trade_keywords = {
            "plumb": 15,
            "fitter": 15,
            "pipefitter": 10,
            "mechanical engineering": 10,
            "gasfitter": 5,
            "machinist": 5,
            "millwright": 5
        }
        
        # Prioritize matching based on active structural context
        if "plumb" in prof_lower:
            trade_keywords["plumb"] = 20
        if "fitter" in prof_lower or "mechanical" in prof_lower:
            trade_keywords["fitter"] = 20
            trade_keywords["mechanical engineering"] = 15

        for kw, points in trade_keywords.items():
            if kw in desc_lower:
                trade_score += points
        
        # Check crucial regulatory/skilled trade certifications
        if "red seal" in desc_lower or "journeyman" in desc_lower:
            trade_score += 10
        if "certificate" in desc_lower or "certified" in desc_lower:
            trade_score += 5
            
        trade_score = min(trade_score, 30)

        # ==================================================
        # 2. EXPERIENCE DEPTH MATCHING (Max 25)
        # ==================================================
        # Extract required years from description using regex (e.g., "5+ years", "3-5 years")
        years_required = 0
        exp_matches = re.findall(r'(\d+)\s*(?:\+|–|-)?\s*year', desc_lower)
        if exp_matches:
            try:
                years_required = max(int(x) for x in exp_matches)
            except ValueError:
                years_required = 0

        # High tier value matching for senior professionals
        if years_required == 0:
            exp_score = 20  # Safe baseline when no explicit requirement stated
        elif years_required >= 10:
            exp_score = 25  # Perfect match for a 20+ year veteran
        elif years_required >= 5:
            exp_score = 22
        else:
            exp_score = 15

        # ==================================================
        # 3. DOMAIN & INDUSTRY SPECIALIZATION (Max 20)
        # ==================================================
        # Weigh targeted heavy industries and operating contexts
        domains = {
            "commercial": 5,
            "industrial": 5,
            "shipyard": 5,
            "maintenance": 4,
            "contractor": 3,
            "construction": 3,
            "infrastructure": 3
        }
        for dom, points in domains.items():
            if dom in desc_lower:
                domain_score += points
        domain_score = min(domain_score, 20)

        # ==================================================
        # 4. COMPLIANCE & MOBILITY INCENTIVES (Max 25)
        # ==================================================
        # Factor in explicit global transition support flags
        if job_metadata.get("visa_sponsored") or "visa" in desc_lower or "sponsor" in desc_lower:
            compliance_score += 10
        if job_metadata.get("work_permit") or "permit" in desc_lower or "authorization" in desc_lower:
            compliance_score += 8
        if job_metadata.get("relocation") or "relocat" in desc_lower:
            compliance_score += 7
            
        # Fallback default value if no metadata flags are passed yet
        if not job_metadata and compliance_score == 0:
            compliance_score = 15

        # Final score accumulation
        api_score = int(trade_score + exp_score + domain_score + compliance_score)
        api_score = max(0, min(api_score, 100))

        # ==================================================
        # ATS REAL CV MATCHING ALGORITHM (Phase 3)
        # ==================================================
        # Compare actual intersection of CV keywords directly with Description text
        match_keywords = [
            "plumbing", "plumber", "fitter", "pipefitter", "mechanical", "engineering", 
            "commercial", "industrial", "maintenance", "installation", "pipelines", 
            "supervision", "machinery", "blueprints", "welding", "valves"
        ]
        
        matched_skills = 0
        total_tracked = 0
        
        for word in match_keywords:
            if word in desc_lower:
                total_tracked += 1
                if word in cv_lower:
                    matched_skills += 1

        cv_match_pct = int((matched_skills / total_tracked) * 100) if total_tracked > 0 else 70
        
        # Strict evaluation: High compatibility threshold
        is_cv_matched = cv_match_pct >= 65 and api_score >= 50

        return {
            "api_score": api_score,
            "cv_match_pct": cv_match_pct,
            "cv_match": is_cv_matched
        }
