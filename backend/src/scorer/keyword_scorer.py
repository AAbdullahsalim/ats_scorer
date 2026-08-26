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
    
    # FIX FOR STREAMING PIPELINE:
    # BM25 IDF collapses when N is too small (e.g., N=2 when streaming 1 CV at a time).
    # We append 15 dummy documents to simulate a batch background corpus, restoring proper IDF math.
    if len(full_corpus) < 10:
        dummy_docs = [["dummy_background_term_for_idf_stability"] for _ in range(15)]
        full_corpus.extend(dummy_docs)

    bm25 = BM25Okapi(full_corpus)
    all_scores = bm25.get_scores(tokenized_query)

    # In real hiring, a top resume contains the technical terms (~25-30% of full JD vocabulary with boilerplates)
    # Saturation threshold maps realistic full technical keyword coverage to 1.0
    saturation_benchmark = max(0.001, float(all_scores[0]))
    
    # Only apply the massive 0.28 discount factor if we are dealing with a large real corpus where IDF values skew.
    # When streaming single CVs with dummy background documents, the theoretical max is the full query self-score.
    if len(corpus_texts) > 5:
        saturation_benchmark *= 0.28
    else:
        # For single streaming, allow a bit of leniency (a resume rarely has EVERY single word in a JD)
        saturation_benchmark *= 0.65
    candidate_raw_scores = all_scores[1:1 + len(corpus_texts)]

    return [
        max(0.0, min(1.0, float(s / saturation_benchmark)))
        for s in candidate_raw_scores
    ]
