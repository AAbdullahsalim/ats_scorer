"""
Semantic similarity scorer using sentence-transformers.
Computes cosine similarity between JD and CV sections.
"""

from typing import Optional

from sentence_transformers import SentenceTransformer, util


class SemanticScorer:
    """Computes dense vector cosine similarity scores."""

    def __init__(self, model: Optional[SentenceTransformer] = None, model_name: str = "all-MiniLM-L6-v2"):
        if model is not None:
            self.model = model
        else:
            self.model = SentenceTransformer(model_name)

    def compute_similarities(
        self, anchor_text: str, target_texts: list[str]
    ) -> list[float]:
        """
        Compute cosine similarity between one anchor text and multiple targets.
        Returns a list of similarity scores in [0.0, 1.0].
        """
        if not anchor_text.strip() or not target_texts:
            return [0.0] * len(target_texts)

        anchor_emb = self.model.encode(anchor_text, convert_to_tensor=True)
        target_embs = self.model.encode(target_texts, convert_to_tensor=True)
        similarities = util.cos_sim(anchor_emb, target_embs)[0].tolist()

        return [max(0.0, float(s)) for s in similarities]
