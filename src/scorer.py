import re
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
from datetime import datetime
from typing import List, Dict

class HybridScorer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print("Loading local vector model (MiniLM-L6-v2)...")
        self.vector_model = SentenceTransformer(model_name)

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'\w+', text.lower())

    def compute_vector_similarity(self, jd_text: str, cv_texts: list[str]) -> list[float]:
        """Calculates cosine similarity and calibrates it to a realistic ATS distribution."""
        jd_embedding = self.vector_model.encode(jd_text, convert_to_tensor=True)
        cv_embeddings = self.vector_model.encode(cv_texts, convert_to_tensor=True)

        similarities = util.cos_sim(jd_embedding, cv_embeddings)[0].tolist()
        
        calibrated = []
        for score in similarities:
            score = max(0.0, float(score))
            scaled = min(1.0, max(0.0, (score - 0.15) / 0.55)) if score > 0.15 else score * 1.5
            calibrated.append(scaled)
            
        return calibrated

    def compute_bm25_scores(self, jd_text: str, cv_texts: list[str]) -> list[float]:
        """Calculates robust BM25 keyword scores without harsh deflation."""
        tokenized_cvs = [self._tokenize(cv) for cv in cv_texts]
        tokenized_jd = self._tokenize(jd_text)

        if not tokenized_jd:
            return [0.5] * len(cv_texts)

        bm25 = BM25Okapi(tokenized_cvs)
        scores = bm25.get_scores(tokenized_jd)
        
        max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0
        normalized = [min(1.0, float(s / max_score)) if max_score > 0 else 0.0 for s in scores]
        return normalized

    def apply_hard_requirement_penalties(self, jd_text: str, candidates: list[dict], base_scores: list[float]) -> list[float]:
        """Applies gentle, realistic penalties instead of crushing scores."""
        jd_lower = jd_text.lower()
        mandatory_keywords = []
        
        if "python" in jd_lower:
            mandatory_keywords.append("python")
        if "nestjs" in jd_lower or "node" in jd_lower:
            mandatory_keywords.extend(["nestjs", "node"])

        if not mandatory_keywords:
            return base_scores

        adjusted_scores = []
        for i, cand in enumerate(candidates):
            full_cv_text = cand["full_text"].lower()
            missing_count = sum(1 for kw in mandatory_keywords if kw not in full_cv_text)
            
            score = base_scores[i]
            if missing_count == 1:
                score *= 0.90  
            elif missing_count >= 2:
                score *= 0.80
                
            adjusted_scores.append(score)

        return adjusted_scores

    def score_candidates(
        self, 
        jd_text: str, 
        candidates: list[dict], 
        vector_weight: float = 0.6, 
        bm25_weight: float = 0.4
    ) -> list[dict]:
        if not candidates:
            return []

        results = []
        jd_embedding = self.vector_model.encode(jd_text, convert_to_tensor=True)

        cv_skills_list = []
        cv_exp_list = []
        cv_full_list = []

        for c in candidates:
            skills = c['sections'].get('skills', '')
            exp = c['sections'].get('experience', '')
            full = c['full_text']
            
            cv_skills_list.append(skills if skills else full)
            cv_exp_list.append(exp if exp else full)
            cv_full_list.append(full)

        skills_sims = self.compute_vector_similarity(jd_text, cv_skills_list)
        exp_sims = self.compute_vector_similarity(jd_text, cv_exp_list)
        full_sims = self.compute_vector_similarity(jd_text, cv_full_list)

        vector_scores = []
        for i in range(len(candidates)):
            weighted_vector = (skills_sims[i] * 0.4) + (exp_sims[i] * 0.4) + (full_sims[i] * 0.2)
            vector_scores.append(weighted_vector)

        bm25_corpus = [f"{cv_skills_list[i]} {cv_exp_list[i]}" for i in range(len(candidates))]
        bm25_scores = self.compute_bm25_scores(jd_text, bm25_corpus)

        raw_final_scores = []
        for i in range(len(candidates)):
            final_score = (vector_scores[i] * vector_weight) + (bm25_scores[i] * bm25_weight)
            boosted_pct = 40.0 + (final_score * 55.0)
            raw_final_scores.append(min(98.0, boosted_pct))

        penalized_scores = self.apply_hard_requirement_penalties(jd_text, candidates, raw_final_scores)

        for i, cand in enumerate(candidates):
            results.append({
                "file_name": cand["file_name"],
                "final_score_pct": round(penalized_scores[i], 2),
                "vector_score_pct": round(vector_scores[i] * 100, 2),
                "bm25_score_pct": round(bm25_scores[i] * 100, 2),
                "sections": cand["sections"]
            })

        return sorted(results, key=lambda x: x["final_score_pct"], reverse=True)


# =====================================================================
# GLOBAL FUNCTIONS
# =====================================================================

SYNONYM_MAP = {
    "aws": ["aws", "amazon web services", "amazon cloud"],
    "gcp": ["gcp", "google cloud"],
    "k8s": ["k8s", "kubernetes"],
    "react": ["react", "reactjs", "react.js"],
    "node.js": ["node.js", "nodejs", "node"],
    "postgres": ["postgres", "postgresql"],
    "python": ["python", "python3"],
    "machine learning": ["machine learning", "ml"],
    "nlp": ["nlp", "natural language processing"],
    "nestjs": ["nestjs", "nest.js", "nest"]
}

def evaluate_must_haves(candidate_text: str, must_haves: List[str]) -> Dict:
    if not must_haves:
        return {"matched": [], "missing": [], "ratio": 1.0}
    
    text_lower = candidate_text.lower()
    matched = []
    missing = []
    
    for skill in must_haves:
        skill_clean = skill.strip().lower()
        aliases = SYNONYM_MAP.get(skill_clean, [skill_clean])
        
        found = False
        for alias in aliases:
            if alias in text_lower or skill_clean in text_lower:
                found = True
                break
                
        if found:
            matched.append(skill)
        else:
            missing.append(skill)
            
    ratio = len(matched) / len(must_haves) if len(must_haves) > 0 else 1.0
    return {
        "matched": matched,
        "missing": missing,
        "ratio": ratio
    }

def apply_must_have_penalty(base_hybrid_score: float, coverage_ratio: float, floor_penalty: float = 0.8) -> float:
    penalty_multiplier = floor_penalty + ((1.0 - floor_penalty) * coverage_ratio)
    return round(base_hybrid_score * penalty_multiplier, 2)

def estimate_candidate_yoe(cv_text_or_sections):
    full_text = ""
    exp_text = ""
    
    if isinstance(cv_text_or_sections, dict):
        exp_text = cv_text_or_sections.get("experience", "")
        full_text = " ".join(cv_text_or_sections.values())
    else:
        full_text = str(cv_text_or_sections)
        exp_text = full_text

    explicit_patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
        r'(?:experience|exp)(?:\s+of)?\s+(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)'
    ]
    
    for pat in explicit_patterns:
        match = re.search(pat, full_text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                if 0 < val < 40:
                    return val
            except ValueError:
                pass

    date_range_pattern = re.compile(
        r'(0[1-9]|1[0-2])/(\d{4})\s*[-–to]+\s*(?:(0[1-9]|1[0-2])/(\d{4})|[Pp]resent|[Cc][Uu][Rr][Rr][Ee][Nn][Tt])|'
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})\s*[-–to]+\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})|[Pp]resent|[Cc][Uu][Rr][Rr][Ee][Nn][Tt])|'
        r'(\d{4})\s*[-–to]+\s*(\d{4}|[Pp]resent|[Cc][Uu][Rr][Rr][Ee][Nn][Tt])',
        re.IGNORECASE
    )

    current_year = datetime.now().year
    current_month = datetime.now().month

    matches = date_range_pattern.findall(exp_text if exp_text.strip() else full_text)
    total_months = 0

    for match in matches:
        start_yr, end_yr = None, None
        start_mo, end_mo = 1, 1

        if match[1]:
            start_mo = int(match[0])
            start_yr = int(match[1])
            if match[3]:
                end_mo = int(match[2])
                end_yr = int(match[3])
            else:
                end_yr = current_year
                end_mo = current_month
        elif match[5]:
            start_yr = int(match[5])
            if match[6]:
                end_yr = int(match[6])
            else:
                end_yr = current_year
                end_mo = current_month
        elif match[7]:
            try:
                start_yr = int(match[7])
                end_str = match[8]
                if re.match(r'pres|curr', end_str, re.IGNORECASE):
                    end_yr = current_year
                    end_mo = current_month
                else:
                    end_yr = int(end_str)
            except ValueError:
                continue

        if start_yr and end_yr:
            duration = (end_yr - start_yr) * 12 + (end_mo - start_mo)
            if 0 < duration <= 60 and duration != 48:
                total_months += duration

    if total_months > 0:
        return round(total_months / 12.0, 1)

    return 0.0

def apply_yoe_modifier(base_score: float, candidate_yoe: float, required_yoe: float) -> float:
    if required_yoe == 0.0:
        return base_score 
    if candidate_yoe >= required_yoe:
        return round(min(99.0, base_score * 1.08), 2)
    if 0 < candidate_yoe < required_yoe:
        return round(base_score * 0.95, 2)
    return base_score