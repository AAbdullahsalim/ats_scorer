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

        # Compute cosine similarity using PyTorch / SentenceTransformers helper
        from sentence_transformers import util
        similarities = util.cos_sim(jd_embedding, cv_embeddings)[0].tolist()
        return [max(0.0, float(score)) for score in similarities]

    def compute_bm25_scores(self, jd_text: str, cv_texts: list[str]) -> list[float]:
        """Calculates BM25 keyword match score normalized to range [0, 1]."""
        tokenized_cvs = [self._tokenize(cv) for cv in cv_texts]
        tokenized_jd = self._tokenize(jd_text)

        bm25 = BM25Okapi(tokenized_cvs)
        doc_scores = bm25.get_scores(tokenized_jd)

        # Min-Max Normalization to bring scores between 0 and 1
        max_score = max(doc_scores) if len(doc_scores) > 0 and max(doc_scores) > 0 else 1.0
        normalized_scores = [float(score / max_score) for score in doc_scores]
        return normalized_scores

    def score_candidates(
        self, 
        jd_text: str, 
        candidates: list[dict], 
        vector_weight: float = 0.6, 
        bm25_weight: float = 0.4
    ) -> list[dict]:
        """
        Combines Dense Vector and BM25 Sparse scores into a final weighted hybrid score.
        vector_weight + bm25_weight should equal 1.0
        """
        if not candidates:
            return []

        # Prepare full text for scoring (Skills section heavily impacts BM25 & Vectors)
        cv_texts = []
        for c in candidates:
            # We weight skills + experience higher by putting them upfront
            skills = c['sections'].get('skills', '')
            exp = c['sections'].get('experience', '')
            combined = f"SKILLS:\n{skills}\n\nEXPERIENCE:\n{exp}\n\nFULL CV:\n{c['full_text']}"
            cv_texts.append(combined)

        # 1. Dense Semantic Vector Scores
        vector_scores = self.compute_vector_similarity(jd_text, cv_texts)

        # 2. Sparse BM25 Keyword Scores
        bm25_scores = self.compute_bm25_scores(jd_text, cv_texts)

        # 3. Score Fusion
        results = []
        for i, cand in enumerate(candidates):
            v_score = vector_scores[i]
            b_score = bm25_scores[i]
            
            # Hybrid Score calculation
            final_score = (v_score * vector_weight) + (b_score * bm25_weight)

            results.append({
                "file_name": cand["file_name"],
                "final_score_pct": round(final_score * 100, 2),
                "vector_score_pct": round(v_score * 100, 2),
                "bm25_score_pct": round(b_score * 100, 2),
                "sections": cand["sections"]
            })

        # Sort descending by final score
        return sorted(results, key=lambda x: x["final_score_pct"], reverse=True)