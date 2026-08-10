from pathlib import Path
from src.parser import ResumeParser
from src.scorer import HybridScorer

def main():
    parser = ResumeParser()
    
    # 1. Load Job Description
    jd_folder = Path("jds")
    jd_files = list(jd_folder.glob("*.pdf")) + list(jd_folder.glob("*.docx")) + list(jd_folder.glob("*.txt"))
    
    if not jd_files:
        print("ERROR: No JD file found in 'jds/' folder.")
        print("Please place a .pdf, .docx, or .txt Job Description in the 'jds/' folder.")
        return

    jd_file = jd_files[0]
    print(f"Loading Job Description: {jd_file.name}")
    
    if jd_file.suffix.lower() == ".txt":
        with open(jd_file, "r", encoding="utf-8") as f:
            jd_text = f.read()
    else:
        jd_parsed = parser.parse(str(jd_file))
        jd_text = jd_parsed["full_text"]

    # 2. Parse Candidate CVs
    cv_folder = Path("sample_cvs")
    cv_files = list(cv_folder.glob("*.pdf")) + list(cv_folder.glob("*.docx"))
    
    if not cv_files:
        print("ERROR: No candidate files found in 'sample_cvs/'.")
        return

    print(f"Parsing {len(cv_files)} candidate CV(s)...")
    candidates = []
    for cv_path in cv_files:
        try:
            parsed_cv = parser.parse(str(cv_path))
            candidates.append(parsed_cv)
        except Exception as e:
            print(f"Failed to parse {cv_path.name}: {e}")

    # 3. Score & Rank Candidates
    scorer = HybridScorer()
    ranked_candidates = scorer.score_candidates(jd_text, candidates)

    # 4. Display Results Table
    print("\n=======================================================")
    print("               CANDIDATE RANKING RESULTS               ")
    print("=======================================================")
    print(f"{'Rank':<5} | {'Candidate File':<35} | {'Match %':<8} | {'Vector %':<8} | {'BM25 %':<8}")
    print("-" * 75)

    for rank, cand in enumerate(ranked_candidates, start=1):
        print(f"{rank:<5} | {cand['file_name'][:35]:<35} | {cand['final_score_pct']:<8}% | {cand['vector_score_pct']:<8}% | {cand['bm25_score_pct']:<8}%")

if __name__ == "__main__":
    main()