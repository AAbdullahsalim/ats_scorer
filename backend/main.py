"""
ATS Scorer v2 — FastAPI Backend.
API routes for JD analysis, CV scoring, and report export.
"""

import os
import sys
import time
import logging

# Ensure packages are importable from backend/
_this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _this_dir)
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional

from config import BACKEND_PORT, CORS_ORIGINS, MAX_CVS_PER_BATCH
from src.parser import parse_cv, parse_jd, extract_skills_from_jd, extract_required_yoe
from src.scorer import ScoringPipeline
from src.llm import (
    LLMClient,
    build_cv_extraction_prompt, build_jd_extraction_prompt,
    parse_cv_extraction, parse_jd_extraction,
)
from src.export import generate_excel_report
from src.models import (
    AnalysisResponse, JDAnalysisResponse,
    HealthResponse, CandidateResult, ParsedCandidate,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === App Setup ===
app = FastAPI(title="ATS Scorer v2", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Lazy-loaded singletons ===
_pipeline: Optional[ScoringPipeline] = None
_llm: Optional[LLMClient] = None
_keybert_model = None


def get_pipeline() -> ScoringPipeline:
    global _pipeline
    if _pipeline is None:
        logger.info("Loading embedding model (first request)...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        _pipeline = ScoringPipeline(model=model)

        # Also init KeyBERT with same model
        global _keybert_model
        from keybert import KeyBERT
        _keybert_model = KeyBERT(model=model)

        logger.info("Model loaded successfully")
    return _pipeline


def get_llm() -> LLMClient:
    global _llm
    if _llm is None:
        _llm = LLMClient()
    return _llm


# === Routes ===

@app.get("/health", response_model=HealthResponse)
async def health_check():
    llm = get_llm()
    return HealthResponse(
        status="ok",
        model_loaded=_pipeline is not None,
        gemini_configured=llm._gemini_available,
        groq_configured=llm._groq_available,
        llm_mode=llm.active_provider,
    )


@app.post("/parse-jd", response_model=JDAnalysisResponse)
async def analyze_jd(file: UploadFile = File(...)):
    """Parse a JD and extract skills + requirements."""
    content = await file.read()
    jd_text = parse_jd(content, file_name=file.filename or "jd")

    # Regex extraction
    must_haves, nice_to_haves = extract_skills_from_jd(
        jd_text, keybert_model=_keybert_model
    )
    required_yoe = extract_required_yoe(jd_text)

    # LLM enhancement
    llm = get_llm()
    llm_enhanced = False

    if llm.is_available:
        prompt = build_jd_extraction_prompt(jd_text)
        raw = llm.call_json(prompt)
        parsed = parse_jd_extraction(raw)

        if parsed:
            llm_enhanced = True
            # Merge LLM results with regex results
            llm_must = parsed.get("must_have_skills", [])
            llm_nice = parsed.get("nice_to_have_skills", [])
            llm_yoe = parsed.get("required_yoe", 0)

            if llm_must:
                # Union of regex + LLM skills
                combined = list(set(must_haves + llm_must))
                must_haves = sorted(combined)
            if llm_nice:
                combined_nice = list(set(nice_to_haves + llm_nice))
                nice_to_haves = sorted(combined_nice)
            if llm_yoe > 0:
                required_yoe = llm_yoe

    return JDAnalysisResponse(
        jd_text=jd_text,
        must_have_skills=must_haves,
        nice_to_have_skills=nice_to_haves,
        required_yoe=required_yoe,
        llm_enhanced=llm_enhanced,
    )


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_candidates(
    jd_file: UploadFile = File(...),
    cv_files: list[UploadFile] = File(...),
    must_have_skills: Optional[str] = Form(None),
    nice_to_have_skills: Optional[str] = Form(None),
    target_yoe: float = Form(0.0),
):
    """Full analysis pipeline: parse JD + CVs, score, rank."""
    start_time = time.time()

    # Enforce batch limit
    if len(cv_files) > MAX_CVS_PER_BATCH:
        cv_files = cv_files[:MAX_CVS_PER_BATCH]

    # Parse JD
    jd_content = await jd_file.read()
    jd_text = parse_jd(jd_content, file_name=jd_file.filename or "jd")
    logger.info(f"JD parsed: {len(jd_text)} chars from '{jd_file.filename}'")

    # Parse skills from form data or extract from JD
    pipeline = get_pipeline()
    llm = get_llm()

    if must_have_skills:
        must_haves = [s.strip() for s in must_have_skills.split(",") if s.strip()]
    else:
        must_haves, _ = extract_skills_from_jd(jd_text, keybert_model=_keybert_model)

    if nice_to_have_skills:
        nice_to_haves = [s.strip() for s in nice_to_have_skills.split(",") if s.strip()]
    else:
        _, nice_to_haves = extract_skills_from_jd(jd_text, keybert_model=_keybert_model)

    # Step 1: Parse all CVs (fast, regex-based)
    candidates: list[ParsedCandidate] = []
    for cv_file in cv_files:
        try:
            cv_content = await cv_file.read()
            parsed = parse_cv(cv_content, file_name=cv_file.filename or "cv")
            logger.info(f"Parsed CV '{cv_file.filename}' -> name: '{parsed.contact.name}', text: {len(parsed.full_text)} chars")
            candidates.append(parsed)
        except Exception as e:
            logger.warning(f"Failed to parse {cv_file.filename}: {e}")

    # Step 2: LLM enhancement (sequential, one per CV)
    if llm.is_available:
        llm.reset_rate_limits()  # Fresh start for this batch
        for i, candidate in enumerate(candidates):
            prompt = build_cv_extraction_prompt(
                candidate.full_text, must_haves
            )
            raw = llm.call_json(prompt)
            logger.info(f"LLM output for CV {i} ('{candidate.file_name}'): {'OK' if raw else 'None'}")
            if raw:
                llm_data = parse_cv_extraction(raw)
                if llm_data:
                    candidates[i] = candidate.model_copy(
                        update={"llm_data": llm_data}
                    )
                    logger.info(f"  -> LLM name: '{llm_data.candidate_name}', YOE: {llm_data.total_yoe}")
                else:
                    logger.warning(f"  -> LLM parse failed for CV {i} ('{candidate.file_name}')")
            else:
                logger.warning(f"  -> No LLM output for CV {i} ('{candidate.file_name}') — using regex fallback")

    # Step 3: Score all candidates
    results = pipeline.score_candidates(
        jd_text=jd_text,
        candidates=candidates,
        must_have_skills=must_haves,
        nice_to_have_skills=nice_to_haves,
        target_yoe=target_yoe,
    )

    elapsed = round(time.time() - start_time, 2)

    jd_analysis = JDAnalysisResponse(
        jd_text=jd_text,
        must_have_skills=must_haves,
        nice_to_have_skills=nice_to_haves,
        required_yoe=target_yoe,
    )

    return AnalysisResponse(
        candidates=results,
        jd_analysis=jd_analysis,
        llm_mode=llm.active_provider,
        processing_time_seconds=elapsed,
    )


@app.post("/export")
async def export_excel(
    jd_file: UploadFile = File(...),
    cv_files: list[UploadFile] = File(...),
    must_have_skills: Optional[str] = Form(None),
    nice_to_have_skills: Optional[str] = Form(None),
    target_yoe: float = Form(0.0),
):
    """Run analysis and return styled Excel report."""
    # Reuse the analyze endpoint logic
    response = await analyze_candidates(
        jd_file=jd_file,
        cv_files=cv_files,
        must_have_skills=must_have_skills,
        nice_to_have_skills=nice_to_have_skills,
        target_yoe=target_yoe,
    )

    excel_bytes = generate_excel_report(response.candidates)

    return StreamingResponse(
        excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=ats_recruitment_report.xlsx"
        },
    )
@app.post("/export-json")
async def export_excel_from_json(candidates: list[CandidateResult]):
    """Generate styled Excel report directly from JSON results."""
    excel_bytes = generate_excel_report(candidates)

    return StreamingResponse(
        excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=ats_recruitment_report.xlsx"
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)
