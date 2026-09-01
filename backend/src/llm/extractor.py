"""
LLM response parser — converts raw LLM JSON into typed Pydantic models.
Handles both old "skills_found" format and new "skill_evaluation" format.
"""

import logging
from typing import Optional

from ..models.schemas import (
    LLMExtraction, SkillMatch, ExperienceEntry, EducationEntry,
)
from ..utils.university_normalizer import normalize_university

logger = logging.getLogger(__name__)


def parse_cv_extraction(raw: Optional[dict]) -> Optional[LLMExtraction]:
    """
    Parse the LLM's CV extraction response into a typed LLMExtraction.
    Supports both:
    - v1 format: "skills_found" (open-ended list)
    - v2 format: "skill_evaluation" (forced per-skill with found=true/false)
    Returns None if parsing fails.
    """
    if not raw or not isinstance(raw, dict):
        return None

    def safe_int(val, default=0):
        try:
            return int(float(val)) if val is not None else default
        except (ValueError, TypeError):
            return default

    def safe_float(val, default=0.0):
        try:
            return float(val) if val is not None else default
        except (ValueError, TypeError):
            return default

    try:
        # Parse skills — support BOTH formats for backward compatibility
        skills = []
        
        # v2 format: skill_evaluation with found=true/false
        skill_eval = raw.get("skill_evaluation", [])
        if skill_eval:
            for s in skill_eval:
                if isinstance(s, dict):
                    # In v2 format, we include ALL skills (found and missing)
                    # The SkillMatch object carries the found status
                    found = s.get("found", True)
                    context = s.get("context", "mentioned")
                    
                    # If found is explicitly false, set context to "missing"
                    if not found:
                        context = "missing"
                    
                    skills.append(SkillMatch(
                        name=str(s.get("name", "")),
                        context=context,
                        evidence=str(s.get("evidence", "")),
                    ))
        else:
            # v1 fallback: skills_found (old open-ended format)
            for s in raw.get("skills_found", []):
                if isinstance(s, dict):
                    skills.append(SkillMatch(
                        name=str(s.get("name", "")),
                        context=str(s.get("context", "mentioned")),
                        evidence=str(s.get("evidence", "")),
                    ))

        # Parse experience entries
        experience = []
        for e in raw.get("experience_entries", []):
            if isinstance(e, dict):
                experience.append(ExperienceEntry(
                    role=str(e.get("role", "")),
                    company=str(e.get("company", "")),
                    start=str(e.get("start", "")),
                    end=str(e.get("end", "")),
                    months=safe_int(e.get("months", 0)),
                    key_work=str(e.get("key_work", "")),
                ))

        # Parse education
        education = []
        for ed in raw.get("education", []):
            if isinstance(ed, dict):
                inst_name = str(ed.get("institution", ""))
                education.append(EducationEntry(
                    degree=str(ed.get("degree", "")),
                    institution=inst_name,
                    year=str(ed.get("year", "")),
                    normalized_institution=normalize_university(inst_name)
                ))

        # Parse certifications
        certs = [str(c) for c in raw.get("certifications", []) if c]

        return LLMExtraction(
            candidate_name=str(raw.get("candidate_name") or "Unknown"),
            email=str(raw.get("email") or ""),
            phone=str(raw.get("phone") or ""),
            linkedin=str(raw.get("linkedin") or ""),
            github=str(raw.get("github") or ""),
            portfolio=str(raw.get("portfolio") or ""),
            location=str(raw.get("location") or ""),
            skills_found=skills,
            experience_entries=experience,
            total_yoe=safe_float(raw.get("total_yoe", 0.0)),
            current_role=str(raw.get("current_role") or ""),
            education=education,
            certifications=certs,
            candidate_summary=str(raw.get("candidate_summary") or ""),
        )

    except Exception as e:
        logger.warning(f"Failed to parse LLM extraction: {e}")
        return None


def parse_jd_extraction(raw: Optional[dict]) -> Optional[dict]:
    """
    Parse the LLM's JD extraction response.
    Returns a dict with must_have_skills, nice_to_have_skills, required_yoe.
    """
    if not raw or not isinstance(raw, dict):
        return None

    try:
        return {
            "must_have_skills": [
                str(s) for s in raw.get("must_have_skills", []) if s
            ],
            "nice_to_have_skills": [
                str(s) for s in raw.get("nice_to_have_skills", []) if s
            ],
            "required_yoe": float(raw.get("required_yoe", 1.0)),
        }
    except Exception as e:
        logger.warning(f"Failed to parse JD extraction: {e}")
        return None
