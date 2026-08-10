import re
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

class HybridScorer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load lightweight CPU-friendly embedding model
        print("Loading local vector model (MiniLM-L6-v2)...")
        self.vector_model = SentenceTransformer(model_name)

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace & lowercasing tokenizer for BM25."""
        return re.findall(r'\w+', text.lower())

    def compute_vector_similarity(self, jd_text: str, cv_texts: list[str]) -> list[float]:
        """Calculates cosine similarity between JD embedding and CV embeddings."""
        jd_embedding = self.vector_model.encode(jd_text, convert_to_tensor=True)
        cv_embeddings = self.vector_model.encode(cv_texts, convert_to_tensor=True)

        from sentence_transformers import util
        similarities = util.cos_sim(jd_embedding, cv_embeddings)[0].tolist()
        return [max(0.0, float(score)) for score in similarities]

    def compute_bm25_scores(self, jd_text: str, cv_texts: list[str]) -> list[float]:
        """Calculates absolute BM25 keyword match score normalized to a Perfect CV."""
        tokenized_cvs = [self._tokenize(cv) for cv in cv_texts]
        tokenized_jd = self._tokenize(jd_text)

        perfect_cv = tokenized_jd
        dummy_corpus = [[] for _ in range(100)] 
        full_corpus = tokenized_cvs + [perfect_cv] + dummy_corpus

        bm25 = BM25Okapi(full_corpus)
        all_scores = bm25.get_scores(tokenized_jd)
        
        cv_scores = all_scores[:len(tokenized_cvs)]
        perfect_score = all_scores[len(tokenized_cvs)]

        normalized_scores = []
        for score in cv_scores:
            if perfect_score > 0:
                norm = max(0.0, min(float(score / perfect_score), 1.0))
            else:
                norm = 0.0
            normalized_scores.append(norm)

        return normalized_scores

    def apply_hard_requirement_penalties(self, jd_text: str, candidates: list[dict], base_scores: list[float]) -> list[float]:
        """
        Phase 3 Extra: Scans for core tech dealbreakers in the JD and penalizes 
        candidates missing mandatory domain tags (e.g., AI/ML for an AI/ML role).
        """
        jd_lower = jd_text.lower()
        
        # Automatically identify mandatory high-value keywords requested in the JD
        mandatory_keywords = []
        if "artificial intelligence" in jd_lower or "ai" in jd_lower or "machine learning" in jd_lower or "ml" in jd_lower:
            mandatory_keywords.extend(["ai", "machine learning", "artificial intelligence", "ml", "tensorflow", "pytorch"])
        if "nestjs" in jd_lower:
            mandatory_keywords.append("nestjs")
        if "next.js" in jd_lower or "nextjs" in jd_lower:
            mandatory_keywords.extend(["next.js", "nextjs"])

        if not mandatory_keywords:
            return base_scores  # No specific hard constraints found

        adjusted_scores = []
        for i, cand in enumerate(candidates):
            full_cv_text = cand["full_text"].lower()
            
            # Check how many mandatory keywords are missing
            missing_count = sum(1 for kw in mandatory_keywords if kw not in full_cv_text)
            
            score = base_scores[i]
            # If they are missing key core stack terms, apply a proportional penalty multiplier
            if missing_count >= 2:
                score *= 0.80  # 20% penalty for missing primary domain requirements
            elif missing_count >= 4:
                score *= 0.65  # 35% heavy penalty
                
            adjusted_scores.append(score)

        return adjusted_scores

    def score_candidates(
        self, 
        jd_text: str, 
        candidates: list[dict], 
        vector_weight: float = 0.6, 
        bm25_weight: float = 0.4
    ) -> list[dict]:
        """
        Combines Dense Vector and BM25 Sparse scores with Section-Weighting & Hard Penalties.
        """
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

        from sentence_transformers import util
        
        skills_embeddings = self.vector_model.encode(cv_skills_list, convert_to_tensor=True)
        exp_embeddings = self.vector_model.encode(cv_exp_list, convert_to_tensor=True)
        full_embeddings = self.vector_model.encode(cv_full_list, convert_to_tensor=True)

        skills_sims = util.cos_sim(jd_embedding, skills_embeddings)[0].tolist()
        exp_sims = util.cos_sim(jd_embedding, exp_embeddings)[0].tolist()
        full_sims = util.cos_sim(jd_embedding, full_embeddings)[0].tolist()

        vector_scores = []
        for i in range(len(candidates)):
            s_score = max(0.0, float(skills_sims[i]))
            e_score = max(0.0, float(exp_sims[i]))
            f_score = max(0.0, float(full_sims[i]))
            
            weighted_vector = (s_score * 0.4) + (e_score * 0.4) + (f_score * 0.2)
            vector_scores.append(weighted_vector)

        bm25_corpus = [f"SKILLS: {cv_skills_list[i]} \n EXPERIENCE: {cv_exp_list[i]}" for i in range(len(candidates))]
        bm25_scores = self.compute_bm25_scores(jd_text, bm25_corpus)

        # 4. Fusion + Hard Requirement Penalty Application
        raw_final_scores = []
        for i in range(len(candidates)):
            v_score = vector_scores[i]
            b_score = bm25_scores[i]
            final_score = (v_score * vector_weight) + (b_score * bm25_weight)
            raw_final_scores.append(final_score)

        # Apply the hard dealbreaker penalties
        penalized_scores = self.apply_hard_requirement_penalties(jd_text, candidates, raw_final_scores)

        for i, cand in enumerate(candidates):
            v_score = vector_scores[i]
            b_score = bm25_scores[i]
            final_score = penalized_scores[i]

            results.append({
                "file_name": cand["file_name"],
                "final_score_pct": round(final_score * 100, 2),
                "vector_score_pct": round(v_score * 100, 2),
                "bm25_score_pct": round(b_score * 100, 2),
                "sections": cand["sections"]
            })

        return sorted(results, key=lambda x: x["final_score_pct"], reverse=True)