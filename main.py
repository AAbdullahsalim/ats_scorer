import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from pathlib import Path
from src.parser import ResumeParser, extract_must_haves_with_keybert, extract_required_yoe
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
    
    jd_text = parser.parse_jd(str(jd_file), file_name=jd_file.name)

    # Auto-extract must-have skills and required YOE from JD
    must_have_skills = extract_must_haves_with_keybert(jd_text)
    target_yoe = extract_required_yoe(jd_text)

    print(f"Auto-Extracted Skills: {', '.join(must_have_skills)}")
    print(f"Required YOE: {target_yoe}")

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

    # 3. Score & Rank Candidates (consolidated pipeline)
    scorer = HybridScorer()
    ranked_candidates = scorer.score_candidates(
        jd_text=jd_text,
        candidates=candidates,
        must_have_skills=must_have_skills,
        target_yoe=target_yoe
    )

    # 4. Display Results Table
    print(f"\n{'='*85}")
    print("                        CANDIDATE RANKING RESULTS")
    print(f"{'='*85}")
    print(f"{'Rank':<5} | {'Candidate File':<35} | {'Match %':<8} | {'YOE':<6} | {'Skills':<8}")
    print("-" * 85)

    for rank, cand in enumerate(ranked_candidates, start=1):
        matched_count = len(cand.get("matched_skills", []))
        total_skills = matched_count + len(cand.get("missing_skills", []))
        skills_str = f"{matched_count}/{total_skills}" if total_skills > 0 else "N/A"
        yoe_str = f"{cand.get('candidate_yoe', 0.0)}"
        
        print(f"{rank:<5} | {cand['file_name'][:35]:<35} | {cand['final_score_pct']:<8}% | {yoe_str:<6} | {skills_str:<8}")

if __name__ == "__main__":
    main()