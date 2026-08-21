"""
Skill context evaluator.
Determines whether each required skill is:
  - Verified (used in experience/projects context)
  - Listed (mentioned in skills section or raw text only)
  - Missing (not found anywhere)

Also handles synonym/alias resolution for tech skills.
"""

import re
from typing import Optional


# Bidirectional synonym map for common tech skill variants
SYNONYM_MAP: dict[str, list[str]] = {
    "aws": ["aws", "amazon web services", "amazon cloud"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "k8s": ["k8s", "kubernetes"],
    "react": ["react", "reactjs", "react.js"],
    "node.js": ["node.js", "nodejs", "node"],
    "postgres": ["postgres", "postgresql"],
    "python": ["python", "python3", "python 3"],
    "machine learning": ["machine learning", "ml"],
    "nlp": ["nlp", "natural language processing"],
    "nestjs": ["nestjs", "nest.js", "nest"],
    "next.js": ["next.js", "nextjs", "next"],
    "vue.js": ["vue.js", "vuejs", "vue"],
    "express.js": ["express.js", "expressjs", "express"],
    "typescript": ["typescript", "ts"],
    "javascript": ["javascript", "js", "es6"],
    "mongodb": ["mongodb", "mongo"],
    "ci/cd": ["ci/cd", "cicd", "ci cd", "continuous integration"],
    "docker": ["docker", "containerization"],
    "graphql": ["graphql", "graph ql"],
    "rest apis": ["rest apis", "restful apis", "rest api", "restful"],
    "sql": ["sql", "structured query language"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", "c sharp"],
}


def get_aliases(skill: str) -> list[str]:
    """Get all known aliases for a skill (bidirectional lookup)."""
    skill_lower = skill.strip().lower()
    aliases = {skill_lower}

    for key, syn_list in SYNONYM_MAP.items():
        syn_lower = [s.lower() for s in syn_list]
        if skill_lower == key or skill_lower in syn_lower:
            aliases.update(syn_lower)
            aliases.add(key)

    return list(aliases)


def _skill_in_text(skill: str, text: str) -> bool:
    """Check if any alias of a skill appears in text (word-boundary aware)."""
    text_lower = text.lower()
    for alias in get_aliases(skill):
        pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
        if re.search(pattern, text_lower):
            return True
    return False


def evaluate_skills(
    sections: dict[str, str],
    skills: list[str],
    llm_skills: Optional[list[dict]] = None,
) -> dict:
    """
    Evaluate each skill's presence and context in the candidate's CV.

    Returns:
        {
            "contextual": [skills verified in experience/projects],
            "stuffed": [skills only listed, not used in context],
            "missing": [skills not found at all],
            "ratio": float (0.0 to 1.0 — fraction of skills found),
            "detail": [{"name": ..., "context": ..., "evidence": ...}]
        }
    """
    if not skills:
        return {
            "contextual": [], "stuffed": [], "missing": [],
            "ratio": 1.0, "detail": [],
        }

    # If LLM already extracted skill data, use that as primary
    if llm_skills:
        return _evaluate_from_llm(skills, llm_skills)

    # Regex-based evaluation
    exp_text = (sections.get("experience", "") or "").lower()
    proj_text = (sections.get("projects", "") or "").lower()
    context_text = f"{exp_text} {proj_text}"

    full_text = " ".join(str(v) for v in sections.values() if v).lower()

    contextual = []
    stuffed = []
    missing = []
    detail = []

    for skill in skills:
        if _skill_in_text(skill, context_text):
            contextual.append(skill)
            detail.append({
                "name": skill, "context": "project",
                "evidence": "Found in experience/projects section",
            })
        elif _skill_in_text(skill, full_text):
            stuffed.append(skill)
            detail.append({
                "name": skill, "context": "mentioned",
                "evidence": "Found in text but not in experience/projects",
            })
        else:
            missing.append(skill)
            detail.append({
                "name": skill, "context": "missing", "evidence": "",
            })

    total_found = len(contextual) + len(stuffed)
    ratio = total_found / len(skills) if skills else 1.0

    return {
        "contextual": contextual,
        "stuffed": stuffed,
        "missing": missing,
        "ratio": ratio,
        "detail": detail,
    }


def _evaluate_from_llm(
    required_skills: list[str],
    llm_skills: list[dict],
) -> dict:
    """Use LLM-extracted skill data for more accurate evaluation."""
    # Build lookup: skill name (lowercase) → context info
    llm_lookup: dict[str, dict] = {}
    for entry in llm_skills:
        name_lower = entry.get("name", "").strip().lower()
        if name_lower:
            llm_lookup[name_lower] = entry
            # Also index aliases
            for alias in get_aliases(name_lower):
                llm_lookup[alias] = entry

    contextual = []
    stuffed = []
    missing = []
    detail = []

    for skill in required_skills:
        skill_lower = skill.strip().lower()
        aliases = get_aliases(skill)

        matched_entry = None
        for alias in aliases:
            if alias in llm_lookup:
                matched_entry = llm_lookup[alias]
                break

        if matched_entry:
            ctx = matched_entry.get("context", "mentioned")
            evidence = matched_entry.get("evidence", "")

            if ctx == "project":
                contextual.append(skill)
            else:
                stuffed.append(skill)

            detail.append({
                "name": skill,
                "context": ctx,
                "evidence": evidence,
            })
        else:
            missing.append(skill)
            detail.append({
                "name": skill, "context": "missing", "evidence": "",
            })

    total_found = len(contextual) + len(stuffed)
    ratio = total_found / len(required_skills) if required_skills else 1.0

    return {
        "contextual": contextual,
        "stuffed": stuffed,
        "missing": missing,
        "ratio": ratio,
        "detail": detail,
    }
