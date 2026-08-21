"""
Test script for verifying ATS Scorer backend logic.
"""
import os
import sys
import asyncio
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from src.parser import parse_cv, parse_jd, extract_skills_from_jd
from src.scorer import ScoringPipeline

async def main():
    print("--- ATS Scorer Backend Test ---")
    
    cv_dir = os.path.join("d:\\projects\\New folder\\ATS_Scorer", "sample_cvs")
    jd_dir = os.path.join("d:\\projects\\New folder\\ATS_Scorer", "jds")
    
    cv_files = []
    if os.path.exists(cv_dir):
        cv_files = [os.path.join(cv_dir, f) for f in os.listdir(cv_dir) if f.endswith(".pdf") or f.endswith(".docx")]
    
    jd_files = []
    if os.path.exists(jd_dir):
        jd_files = [os.path.join(jd_dir, f) for f in os.listdir(jd_dir) if f.endswith(".pdf") or f.endswith(".docx") or f.endswith(".txt")]
        
    print(f"Found {len(cv_files)} CVs and {len(jd_files)} JDs.")
    
    if not cv_files:
        print("No CV files found to test.")
        return
        
    # Use the first JD for testing
    jd_path = jd_files[0] if jd_files else None
    jd_text = "Software Engineer with Python and AWS."
    if jd_path:
        print(f"Parsing JD: {os.path.basename(jd_path)}")
        jd_text = parse_jd(jd_path)
    
    print("\n--- Testing Parser ---")
    candidates = []
    for cv_path in cv_files:
        filename = os.path.basename(cv_path)
        print(f"Parsing CV: {filename}")
        try:
            parsed = parse_cv(cv_path)
            candidates.append(parsed)
            # Check unicode fix and section split
            sec = parsed.sections
            print(f"  Sections extracted: Exp={len(sec.experience)}, Skills={len(sec.skills)}, Edu={len(sec.education)}")
            print(f"  Contact: {parsed.contact.name} | {parsed.contact.email}")
        except Exception as e:
            print(f"  ERROR parsing {filename}: {e}")

    print("\n--- Testing Scorer ---")
    print("Loading pipeline...")
    pipeline = ScoringPipeline()
    
    must_have = ["Python", "AWS"]
    nice_have = ["Docker"]
    
    print("Scoring candidates...")
    results = pipeline.score_candidates(
        jd_text=jd_text,
        candidates=candidates,
        must_have_skills=must_have,
        nice_to_have_skills=nice_have,
        target_yoe=2.0
    )
    
    print("\n--- Results ---")
    for r in results:
        print(f"Candidate: {r.candidate_name} ({os.path.basename(r.file_name)})")
        print(f"  Score: {r.final_score_pct}%")
        print(f"  YOE: {r.candidate_yoe}")
        print(f"  Verified skills: {r.contextual_skills}")
        print(f"  Missing skills: {r.missing_skills}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
