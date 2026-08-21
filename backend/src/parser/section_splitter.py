"""
Universal section splitter for CV documents.
Fixes Bug #2: sections swapped/misclassified due to heading detection failures.

Strategy:
1. Multi-signal heading detection (keyword match, bold, caps, length)
2. Fuzzy matching for non-standard headings
3. Content-type heuristics (skill lists vs experience blocks)
4. Fallback: if sections are empty, reclassify based on content patterns
"""

import re
from typing import Optional


# Canonical section keywords — expanded to handle more CV formats
SECTION_KEYWORDS: dict[str, list[str]] = {
    "experience": [
        "experience", "work history", "employment history",
        "professional experience", "career history", "work experience",
        "employment", "work background", "internship", "internships",
        "professional background", "relevant experience",
        "professional history", "career", "positions held",
        "work", "professional journey", "professional profile",
    ],
    "skills": [
        "skills", "technical skills", "competencies",
        "core qualifications", "technologies", "tech stack",
        "tools & technologies", "tools and technologies",
        "expertise", "areas of expertise", "key skills",
        "proficiencies", "technical proficiencies",
        "technical expertise", "what i know",
        "tools", "languages & frameworks", "languages and tools",
        "technical competencies", "core skills", "skill set",
    ],
    "education": [
        "education", "academic background", "degrees",
        "qualifications", "educational background",
        "academic qualifications", "academics",
        "academic history", "education & certifications",
        "education and certifications", "educational qualifications",
    ],
    "projects": [
        "projects", "project", "project experience",
        "key projects", "selected projects", "personal projects",
        "academic projects", "relevant projects", "major projects",
        "portfolio", "notable projects",
    ],
    "summary": [
        "summary", "professional summary", "about me",
        "profile", "executive summary", "career objective",
        "objective", "overview", "about", "introduction",
        "personal statement", "career summary",
    ],
    "certifications": [
        "certifications", "certificates", "licenses",
        "professional certifications", "credentials",
        "certifications & training", "training",
    ],
}


def _normalize_heading_text(line: str) -> str:
    """
    Normalize a potential heading line for matching.
    Handles spaced-out letters (E X P E R I E N C E → experience),
    trailing colons/dashes, and decorative characters.
    """
    # Remove spaced-out letters: "E X P E R I E N C E" → "EXPERIENCE"
    collapsed = re.sub(r"\b([a-zA-Z])\s+(?=[a-zA-Z]\b)", r"\1", line.strip())

    # Lowercase and strip decorators
    clean = collapsed.lower()
    clean = re.sub(r"[:\-_•·–—|►▸▶]+$", "", clean).strip()
    clean = re.sub(r"^[:\-_•·–—|►▸▶]+", "", clean).strip()

    return clean


def classify_heading(
    line: str,
    is_bold: bool = False,
    is_heading_style: bool = False,
    font_size: float = 0.0,
    median_font_size: float = 11.0,
) -> tuple[bool, str]:
    """
    Multi-signal heading classifier with lower thresholds than v1.

    Returns (is_heading, canonical_section_name).
    A heading is accepted if it scores >= 2 (was 3 in v1).
    """
    raw = line.strip()
    if not raw or len(raw) > 70:
        return False, ""

    normalized = _normalize_heading_text(line)

    # Try matching against keyword lists
    matched_section: Optional[str] = None
    for sec_name, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if (
                normalized == kw
                or normalized.startswith(kw + " ")
                or normalized.startswith(kw + ":")
                or normalized.endswith(" " + kw)
            ):
                matched_section = sec_name
                break
        if matched_section:
            break

    if not matched_section:
        return False, ""

    # Map certifications to education for scoring purposes
    if matched_section == "certifications":
        matched_section = "education"

    # Score the heading confidence (lowered threshold from 3 to 2)
    score = 0

    if is_bold or is_heading_style:
        score += 2

    if raw.isupper() or _normalize_heading_text(line).isupper():
        score += 2

    if raw.istitle():
        score += 1

    if len(normalized) < 40:
        score += 1

    if font_size > 0 and font_size > median_font_size * 1.1:
        score += 1

    # Exact keyword match gets a strong bonus
    all_keywords = [kw for kws in SECTION_KEYWORDS.values() for kw in kws]
    if normalized in all_keywords:
        score += 2

    return (score >= 2), matched_section


def _compute_median_font_size(blocks: list[dict]) -> float:
    """Compute median font size across all blocks for heading detection."""
    sizes = [b.get("font_size", 11.0) for b in blocks if b.get("font_size", 0) > 0]
    if not sizes:
        return 11.0
    sizes.sort()
    mid = len(sizes) // 2
    return sizes[mid]


def _looks_like_skill_list(text: str) -> bool:
    """
    Heuristic: does this text block look like a skills/tech list?
    Checks for comma-separated items, category labels (Languages:, Tools:), etc.
    """
    lines = text.strip().split("\n")
    if not lines:
        return False

    skill_indicators = 0
    for line in lines[:10]:
        line_lower = line.lower().strip()

        # "Languages: Python, Java, SQL" pattern
        if re.match(r"^[\w\s/&]+:\s+[\w\s,.\-+#]+", line_lower):
            skill_indicators += 2

        # Comma-heavy lines with tech words
        comma_count = line.count(",")
        if comma_count >= 3:
            skill_indicators += 1

        # Lines that are just tech names separated by pipes or bullets
        if re.match(r"^[\w\s.+#]+(?:\s*[|•·,]\s*[\w\s.+#]+){2,}", line_lower):
            skill_indicators += 1

    return skill_indicators >= 3


def _looks_like_experience_block(text: str) -> bool:
    """
    Heuristic: does this text block look like work experience?
    Checks for date ranges, job titles, company names.
    """
    date_pattern = re.compile(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"Present|Current|20\d{2}|19\d{2})\b",
        re.IGNORECASE,
    )
    role_pattern = re.compile(
        r"\b(?:engineer|developer|architect|lead|senior|junior|"
        r"manager|intern|consultant|analyst|designer|specialist)\b",
        re.IGNORECASE,
    )

    date_hits = len(date_pattern.findall(text[:500]))
    role_hits = len(role_pattern.findall(text[:500]))

    return date_hits >= 2 and role_hits >= 1


def split_blocks_into_sections(blocks: list[dict]) -> dict[str, str]:
    """
    Split document blocks into semantic sections.

    Strategy:
    1. Detect headings using multi-signal classification
    2. Assign subsequent content to detected sections
    3. Post-process: if skills section is empty but experience starts
       with a skill list, reclassify that content
    """
    sections: dict[str, list[str]] = {
        "summary": [],
        "experience": [],
        "skills": [],
        "education": [],
        "projects": [],
        "other": [],
    }

    current_section = "other"
    median_font = _compute_median_font_size(blocks)

    for b in blocks:
        text = b["text"]
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

        for line in lines:
            is_header, sec_name = classify_heading(
                line=line,
                is_bold=b.get("is_bold", False),
                is_heading_style=b.get("is_heading_style", False),
                font_size=b.get("font_size", 0.0),
                median_font_size=median_font,
            )

            if is_header:
                current_section = sec_name
                continue

            if current_section in sections:
                sections[current_section].append(line)
            else:
                sections["other"].append(line)

    # === POST-PROCESSING: Content-based reclassification ===
    result = {k: "\n".join(v).strip() for k, v in sections.items()}
    result = _reclassify_misplaced_content(result)

    return result


def _reclassify_misplaced_content(sections: dict[str, str]) -> dict[str, str]:
    """
    Fix Bug #2: Reclassify content that ended up in the wrong section.

    Cases handled:
    - Skills list dumped into experience → move to skills
    - Summary text in other → move to summary
    - Experience in other → move to experience
    """
    exp_text = sections.get("experience", "")
    skills_text = sections.get("skills", "")
    other_text = sections.get("other", "")
    summary_text = sections.get("summary", "")

    # Case 1: Experience section starts with a skill list
    if exp_text and not skills_text:
        exp_lines = exp_text.split("\n")
        # Check first ~10 lines for skill-list pattern
        first_chunk = "\n".join(exp_lines[:10])
        if _looks_like_skill_list(first_chunk):
            # Find where the actual experience starts (date ranges)
            split_idx = 0
            for i, line in enumerate(exp_lines):
                if re.search(
                    r"\b(?:20\d{2}|19\d{2}|Present|Current)\b", line, re.IGNORECASE
                ):
                    split_idx = i
                    break

            if split_idx > 0:
                sections["skills"] = "\n".join(exp_lines[:split_idx]).strip()
                sections["experience"] = "\n".join(exp_lines[split_idx:]).strip()

    # Case 2: "Other" has experience-like content but experience is empty
    if not sections.get("experience", "") and other_text:
        if _looks_like_experience_block(other_text):
            sections["experience"] = other_text
            sections["other"] = ""

    # Case 3: "Other" has summary-like content but summary is empty
    if not summary_text and other_text:
        other_lines = other_text.split("\n")
        for i, line in enumerate(other_lines[:3]):
            if len(line) > 80 and re.search(
                r"\b\d+\+?\s*(?:years?|yrs?)\b", line, re.IGNORECASE
            ):
                sections["summary"] = line
                remaining = "\n".join(other_lines[:i] + other_lines[i + 1:]).strip()
                sections["other"] = remaining
                break

    return sections
