import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from pathlib import Path
from src.parser import ResumeParser, extract_must_haves_with_keybert, extract_skills_dual, extract_required_yoe
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
    must_have_skills, nice_to_haves = extract_skills_dual(jd_text)
    target_yoe = extract_required_yoe(jd_text)

    print(f"Auto-Extracted Must-Haves: {', '.join(must_have_skills)}")
    print(f"Auto-Extracted Bonus Skills: {', '.join(nice_to_haves)}")
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
        nice_to_have_skills=nice_to_haves,
        target_yoe=target_yoe
    )

    # 4. Display Results Table
    print(f"\n{'='*130}")
    print("                                      CANDIDATE RANKING & AUDIT RESULTS")
    print(f"{'='*130}")
    print(f"{'Rank':<5} | {'Candidate File':<30} | {'Match %':<8} | {'YOE':<6} | {'Ver/Stuf':<9} | {'Skill Pt':<8} | {'R-Exp Pt':<8} | {'O-Exp Pt':<8} | {'Keywd Pt':<8}")
    print("-" * 130)

    for rank, cand in enumerate(ranked_candidates, start=1):
        ctx_len = len(cand.get("contextual_skills", []))
        stuf_len = len(cand.get("stuffed_skills", []))
        skills_str = f"{ctx_len}V/{stuf_len}S"
        
        yoe_str = f"{cand.get('candidate_yoe', 0.0)}"
        audit = cand.get("audit", {})
        subscores = audit.get("subscores", {})
        
        sp = subscores.get("skill_match", 0)
        rp = subscores.get("recent_exp", 0)
        op = subscores.get("older_exp", 0)
        kp = subscores.get("bm25_keyword", 0)
        
        print(f"{rank:<5} | {cand['file_name'][:30]:<30} | {cand['final_score_pct']:<8}% | {yoe_str:<6} | {skills_str:<9} | {sp:<8} | {rp:<8} | {op:<8} | {kp:<8}")

if __name__ == "__main__":
    main()