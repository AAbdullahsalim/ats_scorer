"""
BM25 keyword scorer using rank_bm25.
Computes sparse keyword relevance between JD and CV text.
"""

import re

from rank_bm25 import BM25Okapi
from config import BM25_SATURATION_MULTIPLIER, BM25_MIN_DUMMY_DOCS


def _tokenize(text: str) -> list[str]:
    """Simple word tokenizer for BM25."""
    return re.findall(r"\w+", text.lower())


def compute_bm25_scores(
    query_text: str, corpus_texts: list[str]
) -> list[float]:
    """
    Compute normalized BM25 scores for a query against a corpus.
    Normalized against ideal query self-score so scores reflect absolute keyword relevance
    rather than relative batch scaling.
    """
    tokenized_corpus = [_tokenize(t) for t in corpus_texts]
    tokenized_query = _tokenize(query_text)

    if not tokenized_query or not corpus_texts:
        return [0.0] * len(corpus_texts)

    # Ensure no empty documents (BM25 can crash on empty)
    for i, doc in enumerate(tokenized_corpus):
        if not doc:
            tokenized_corpus[i] = ["empty"]

    # Prepend query itself to the corpus as the gold-standard ideal document
    full_corpus = [tokenized_query] + tokenized_corpus
    
    # Pad with dummy documents to simulate a large background corpus.
    # This prevents IDF collapse when N is small (e.g. streaming 1 CV).
    if len(full_corpus) < BM25_MIN_DUMMY_DOCS:
        needed = BM25_MIN_DUMMY_DOCS - len(full_corpus)
        dummy_docs = [["dummy_background_term_for_idf_stability"] for _ in range(needed)]
        full_corpus.extend(dummy_docs)

    bm25 = BM25Okapi(full_corpus)
    all_scores = bm25.get_scores(tokenized_query)

    # In real hiring, a top resume contains the technical terms (~25-30% of full JD vocabulary with boilerplates)
    # Saturation threshold maps realistic full technical keyword coverage to 1.0
    saturation_benchmark = max(0.001, float(all_scores[0]))
    
    # Use fixed saturation multiplier from config (0.45)
    # This ensures consistency regardless of batch size
    saturation_benchmark *= BM25_SATURATION_MULTIPLIER
    
    candidate_raw_scores = all_scores[1:1 + len(corpus_texts)]

    return [
        max(0.0, min(1.0, float(s / saturation_benchmark)))
        for s in candidate_raw_scores
    ]
