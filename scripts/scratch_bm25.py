import re
from rank_bm25 import BM25Okapi

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())

def compute_bm25_scores(query_text: str, corpus_texts: list[str]) -> list[float]:
    tokenized_corpus = [_tokenize(t) for t in corpus_texts]
    tokenized_query = _tokenize(query_text)

    if not tokenized_query or not corpus_texts:
        return [0.0] * len(corpus_texts)

    for i, doc in enumerate(tokenized_corpus):
        if not doc:
            tokenized_corpus[i] = ["empty"]

    full_corpus = [tokenized_query] + tokenized_corpus
    
    if len(full_corpus) < 10:
        dummy_docs = [["dummy_background_term_for_idf_stability"] for _ in range(15)]
        full_corpus.extend(dummy_docs)

    bm25 = BM25Okapi(full_corpus)
    all_scores = bm25.get_scores(tokenized_query)

    print("all_scores:", all_scores)

    saturation_benchmark = max(0.001, float(all_scores[0])) * 0.28
    print("saturation_benchmark:", saturation_benchmark)
    
    candidate_raw_scores = all_scores[1:1 + len(corpus_texts)]
    print("candidate_raw_scores:", candidate_raw_scores)

    return [
        max(0.0, min(1.0, float(s / saturation_benchmark)))
        for s in candidate_raw_scores
    ]

# test
jd = "We are looking for a software engineer with python and java experience and docker and AWS and CI/CD."
cv = "I am a software engineer. I know python and java. I have used docker."
scores = compute_bm25_scores(jd, [cv])
print("Final normalized scores:", scores)
