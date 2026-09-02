import os
import sys
import asyncio
from pathlib import Path

from src.scorer.pipeline import ScoringPipeline
from src.models.schemas import ParsedCandidate, ContactInfo

def dummy_parse(path):
    import fitz
    doc = fitz.open(path)
    return " ".join(page.get_text() for page in doc)

def main():
    scorer = ScoringPipeline()
    
    cv_paths = [
        Path("sample_cvs/zain_iqbal_cv.pdf").resolve(),
        Path("sample_cvs/SyedMoosaResume.pdf").resolve()
    ]
    
    jd_text = """
    We are looking for a Senior Python Developer with experience in React and AWS.
    Must have 5+ years of experience building scalable backend APIs using FastAPI or Django.
    Experience with Docker and CI/CD pipelines is required.
    """
    
    candidates = []
    
    for path in cv_paths:
        text = dummy_parse(str(path))
        candidates.append(ParsedCandidate(
            file_name=path.name,
            full_text=text,
            sections={"experience": text, "projects": text, "skills": text},
            llm_data=None,
            contact=ContactInfo(name=path.name)
        ))
        
    required_skills = ["Python", "FastAPI", "AWS", "React", "Docker"]
    nice_skills = ["Django", "CI/CD"]
    target_yoe = 5
    
    print("=" * 60)
    print("SCORING MECHANICS PROOF")
    print("=" * 60)
    
    results = scorer.score_candidates(
        jd_text=jd_text,
        candidates=candidates,
        must_have_skills=required_skills,
        nice_to_have_skills=nice_skills,
        target_yoe=target_yoe
    )
    
    for res in results:
        print(f"\n--- CANDIDATE: {res.candidate_name or res.file_name} ---")
        print(f"Final Score: {res.final_score_pct}%")
        print(f"Calculated YOE: {res.candidate_yoe}")
        print("\n[AI SEMANTIC & KEYWORD SUBSCORES]")
        print(f"  - BM25 (Keywords): {res.audit.subscores.bm25_keyword} pts")
        print(f"  - Recent Job Similarity (AI): {res.audit.subscores.recent_exp} pts")
        print(f"  - Older Job Similarity (AI): {res.audit.subscores.older_exp} pts")
        print(f"  - Skills Section Similarity (AI): {res.audit.subscores.skill_match} pts")
        
        print("\n[SKILLS FOUND VS LISTED VS MISSING]")
        print(f"  - Contextual (Proved in Experience): {', '.join(res.contextual_skills) if res.contextual_skills else 'None'}")
        print(f"  - Listed Only (Stuffed): {', '.join(res.stuffed_skills) if res.stuffed_skills else 'None'}")
        print(f"  - Missing Skills: {', '.join(res.missing_skills) if res.missing_skills else 'None'}")

if __name__ == "__main__":
    main()
