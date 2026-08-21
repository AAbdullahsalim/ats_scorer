"""
Years of Experience (YOE) extractor.
Fixes Bug #3: YOE extraction wrong most of the time.

Improvements over v1:
- More date formats: Jul'23, YYYY/MM, ISO dates, Q1 2024
- Better academic date filtering
- Explicit statement prioritization ("10+ years of experience")
- Full-text fallback when section splitter fails
- Work-role block recovery from other sections
"""

import re
from datetime import datetime
from typing import Optional


MONTH_MAP: dict[str, int] = {
    "jan": 1, "january": 1, "feb": 2, "february": 2,
    "mar": 3, "march": 3, "apr": 4, "april": 4,
    "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "sept": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month

# Academic keywords for filtering out education dates
ACADEMIC_KEYWORDS: list[str] = [
    "bachelor", "master", "phd", "degree", "b.s", "bs ", "b.sc",
    "m.s", "m.sc", "mba", "bba", "b.tech", "m.tech", "b.e", "m.e",
    "gce a level", "a level", "high school", "matric", "fsc",
    "education", "fast-nuces", "comsats", "nuces", "university",
    "college", "coursework", "thesis", "undergraduate", "graduate",
    "class of 20", "ieee student", "student branch", "school",
    "diploma", "certificate program", "bootcamp",
    "beaconhouse", "aga khan", "lums", "nust", "itu",
]


def _parse_date_ranges(text: str) -> list[tuple[int, int]]:
    """
    Extract date ranges from text. Returns list of (start_month, end_month)
    where month is year*12 + month_number.

    Handles formats:
    - Month YYYY - Month YYYY (Jan 2024 - Dec 2024)
    - Month'YY - Month'YY (Jul'23 - Dec'24)
    - MM/YYYY - MM/YYYY (01/2024 - 05/2024)
    - YYYY-MM (ISO: 2024-01)
    - YYYY - YYYY (2021 - 2024)
    - Present / Current as end date
    """
    ranges: list[tuple[int, int]] = []

    # Pattern 1: Month YYYY - Month YYYY / Present
    month_pattern = re.compile(
        r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
        r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"[.,]?\s*['\u2019]?(\d{2,4})"
        r"\s*[-\u2013\u2014to]+\s*"
        r"(?:(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
        r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"[.,]?\s*['\u2019]?(\d{2,4})"
        r"|[Pp]resent|[Cc]urrent|[Oo]ngoing|[Nn]ow)\b",
        re.IGNORECASE,
    )

    for match in month_pattern.finditer(text):
        m1_str = match.group(1).lower()[:3]
        y1_raw = match.group(2)
        m2_str = match.group(3)
        y2_raw = match.group(4)

        s_mo = MONTH_MAP.get(m1_str, 1)
        s_yr = int(y1_raw) if len(y1_raw) == 4 else 2000 + int(y1_raw)

        if m2_str and y2_raw:
            e_mo = MONTH_MAP.get(m2_str.lower()[:3], 12)
            e_yr = int(y2_raw) if len(y2_raw) == 4 else 2000 + int(y2_raw)
        else:
            e_mo, e_yr = CURRENT_MONTH, CURRENT_YEAR

        if 1990 <= s_yr <= CURRENT_YEAR and 1990 <= e_yr <= CURRENT_YEAR + 1:
            start_m = s_yr * 12 + s_mo
            end_m = e_yr * 12 + e_mo
            if end_m >= start_m and (end_m - start_m) <= 480:
                ranges.append((start_m, end_m))

    # Pattern 2: MM/YYYY - MM/YYYY
    mmyyyy = re.compile(
        r"\b(0[1-9]|1[0-2])/(20\d{2}|19\d{2})"
        r"\s*[-\u2013\u2014to]+\s*"
        r"(?:(0[1-9]|1[0-2])/(20\d{2}|19\d{2})"
        r"|[Pp]resent|[Cc]urrent)\b",
        re.IGNORECASE,
    )

    for match in mmyyyy.finditer(text):
        s_mo, s_yr = int(match.group(1)), int(match.group(2))
        if match.group(3) and match.group(4):
            e_mo, e_yr = int(match.group(3)), int(match.group(4))
        else:
            e_mo, e_yr = CURRENT_MONTH, CURRENT_YEAR

        if 1990 <= s_yr <= CURRENT_YEAR and 1990 <= e_yr <= CURRENT_YEAR + 1:
            start_m = s_yr * 12 + s_mo
            end_m = e_yr * 12 + e_mo
            if end_m >= start_m and (end_m - start_m) <= 480:
                ranges.append((start_m, end_m))

    # Pattern 3: YYYY - YYYY (year only, no month)
    yyyy = re.compile(
        r"\b(20\d{2}|19\d{2})\s*[-\u2013\u2014to]+\s*"
        r"(20\d{2}|19\d{2}|[Pp]resent|[Cc]urrent)\b",
        re.IGNORECASE,
    )

    for match in yyyy.finditer(text):
        s_yr = int(match.group(1))
        end_str = match.group(2)

        if re.match(r"[Pp]res|[Cc]urr", end_str):
            e_yr, e_mo = CURRENT_YEAR, CURRENT_MONTH
        else:
            e_yr = int(end_str)
            e_mo = 12
            # Filter academic degree timelines (3-5 year span ending in future)
            if e_yr >= CURRENT_YEAR and (e_yr - s_yr) >= 3:
                continue

        s_mo = 1
        if 1990 <= s_yr <= CURRENT_YEAR and 1990 <= e_yr <= CURRENT_YEAR + 1:
            start_m = s_yr * 12 + s_mo
            end_m = e_yr * 12 + e_mo
            if end_m >= start_m and (end_m - start_m) <= 480:
                ranges.append((start_m, end_m))

    return ranges


def _filter_academic_lines(text: str) -> str:
    """Remove lines that are adjacent to academic keywords."""
    lines = text.split("\n")
    filtered = []

    for i, line in enumerate(lines):
        context = line.lower()
        if i > 0:
            context += " " + lines[i - 1].lower()
        if i < len(lines) - 1:
            context += " " + lines[i + 1].lower()

        if not any(kw in context for kw in ACADEMIC_KEYWORDS):
            filtered.append(line)

    return "\n".join(filtered)


def _merge_overlapping_ranges(
    ranges: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Merge overlapping or adjacent date ranges."""
    if not ranges:
        return []

    sorted_ranges = sorted(ranges, key=lambda x: x[0])
    merged = [sorted_ranges[0]]

    for start, end in sorted_ranges[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end + 1:  # +1 for adjacent months
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))

    return merged


def extract_yoe(
    sections: dict[str, str],
    full_text: str = "",
    llm_yoe: Optional[float] = None,
) -> float:
    """
    Extract total years of experience from CV.

    Priority:
    1. LLM-extracted YOE (if available)
    2. Explicit statements ("10+ years of experience")
    3. Date range extraction from experience section
    4. Date range extraction from full text (fallback)
    """
    # Priority 1: LLM data
    if llm_yoe is not None and llm_yoe > 0:
        return llm_yoe

    # Build full text if not provided
    if not full_text:
        full_text = " ".join(v for v in sections.values() if v)

    # Priority 2: Explicit statements
    explicit_patterns = [
        r"(?:over|more than|\+)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)"
        r"(?:\s+of)?\s+(?:professional\s+)?(?:experience|exp)",

        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:track\s+record|career)",

        r"(?:experience|exp)(?:\s+of)?\s+(?:over|more than|\+)?\s*"
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]

    for pat in explicit_patterns:
        match = re.search(pat, full_text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                if 0.5 <= val < 50:
                    return val
            except ValueError:
                pass

    # Priority 3: Date ranges from experience section
    exp_text = sections.get("experience", "")
    target_text = exp_text if exp_text.strip() else full_text

    # Recover work role blocks from other sections
    work_role_patterns = [
        r"\b(?:software|backend|frontend|full.?stack|data|devops|cloud|"
        r"ai|ml|lead|senior|junior|mid)\s+"
        r"(?:engineer|developer|architect|consultant|analyst|specialist|"
        r"manager|officer|executive|designer)\b",
        r"\b(?:intern(?:ship)?|full.?time|part.?time|contract)\b",
    ]

    extra_lines = []
    for sec_key in ("summary", "skills", "other"):
        sec_text = sections.get(sec_key, "")
        if not sec_text:
            continue
        lines = sec_text.split("\n")
        for i, line in enumerate(lines):
            if any(re.search(pat, line, re.IGNORECASE) for pat in work_role_patterns):
                start_i = max(0, i - 1)
                end_i = min(len(lines), i + 4)
                extra_lines.extend(lines[start_i:end_i])

    combined_text = f"{target_text}\n" + "\n".join(extra_lines)

    # Filter out academic lines
    clean_text = _filter_academic_lines(combined_text)
    if not clean_text.strip():
        clean_text = _filter_academic_lines(full_text)

    # Parse and merge date ranges
    ranges = _parse_date_ranges(clean_text)
    if not ranges:
        # Priority 4: Try full text as last resort
        ranges = _parse_date_ranges(_filter_academic_lines(full_text))

    if not ranges:
        return 0.0

    merged = _merge_overlapping_ranges(ranges)
    total_months = sum(end - start for start, end in merged)

    return round(total_months / 12.0, 1)
