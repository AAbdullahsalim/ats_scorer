"""
BM25 keyword scorer using rank_bm25.
Computes sparse keyword relevance between JD and CV text.
"""

import re

from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    """Simple word tokenizer for BM25."""
    return re.findall(r"\w+", text.lower())


def compute_bm25_scores(
    query_text: str, corpus_texts: list[str]
) -> list[float]:
    """
    Compute normalized BM25 scores for a query against a corpus.
    Returns scores in [0.0, 1.0] range.
    """
    tokenized_corpus = [_tokenize(t) for t in corpus_texts]
    tokenized_query = _tokenize(query_text)

    if not tokenized_query:
        return [0.0] * len(corpus_texts)

    # Ensure no empty documents (BM25 can crash on empty)
    for i, doc in enumerate(tokenized_corpus):
        if not doc:
            tokenized_corpus[i] = ["empty"]

    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenized_query)

    max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0

    return [
        min(1.0, float(s / max_score)) if max_score > 0 else 0.0
        for s in scores
    ]
