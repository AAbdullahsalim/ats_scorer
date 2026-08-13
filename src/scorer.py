import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

import re
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set

# =====================================================================
# SYNONYM MAP & BIDIRECTIONAL SKILL MATCHING
# =====================================================================

SYNONYM_MAP = {
    "aws": ["aws", "amazon web services", "amazon cloud"],
    "gcp": ["gcp", "google cloud"],
    "k8s": ["k8s", "kubernetes"],
    "react": ["react", "reactjs", "react.js"],
    "node.js": ["node.js", "nodejs", "node"],
    "postgres": ["postgres", "postgresql"],
    "python": ["python", "python3"],
    "machine learning": ["machine learning", "ml"],
    "nlp": ["nlp", "natural language processing"],
    "nestjs": ["nestjs", "nest.js", "nest"]
}

def get_aliases_for_skill(skill: str) -> List[str]:
    """Bidirectional synonym lookup: maps any skill variant to all known aliases."""
    skill_clean = skill.strip().lower()
    aliases = {skill_clean}

    for key, syn_list in SYNONYM_MAP.items():
        syn_lower = [s.lower() for s in syn_list]
        if skill_clean == key or skill_clean in syn_lower:
            aliases.update(syn_lower)
            aliases.add(key)

    return list(aliases)

def evaluate_skill_context(candidate_sections: Dict[str, str], skills: List[str]) -> Dict:
    """
    Evaluate skills with context.
    If a skill is found in 'experience' or 'projects', it's 'contextual' (Verified).
    If it's only found in 'skills' or the raw text without context, it's 'stuffed' (Listed).
    """
    if not skills:
        return {"contextual": [], "stuffed": [], "missing": [], "ratio": 1.0}

    exp_text = candidate_sections.get("experience", "").lower()
    proj_text = candidate_sections.get("projects", "").lower()
    context_text = exp_text + " " + proj_text
    
    # Fallback to full text if sections are completely empty
    full_text = " ".join([str(v) for v in candidate_sections.values() if v]).lower()

    contextual = []
    stuffed = []
    missing = []

    for skill in skills:
        aliases = get_aliases_for_skill(skill)
        found_in_context = False
        found_anywhere = False

        for alias in aliases:
            pattern = r'(?<!\w)' + re.escape(alias) + r'(?!\w)'
            if context_text and re.search(pattern, context_text):
                found_in_context = True
                break
            if re.search(pattern, full_text):
                found_anywhere = True

        if found_in_context:
            contextual.append(skill)
        elif found_anywhere:
            stuffed.append(skill)
        else:
            missing.append(skill)

    total_found = len(contextual) + len(stuffed)
    ratio = total_found / len(skills) if len(skills) > 0 else 1.0
    return {"contextual": contextual, "stuffed": stuffed, "missing": missing, "ratio": ratio}



# =====================================================================
# UNIVERSAL YOE EXTRACTION ENGINE
# =====================================================================

MONTH_MAP = {
    'jan': 1, 'january': 1,
    'feb': 2, 'february': 2,
    'mar': 3, 'march': 3,
    'apr': 4, 'april': 4,
    'may': 5,
    'jun': 6, 'june': 6,
    'jul': 7, 'july': 7,
    'aug': 8, 'august': 8,
    'sep': 9, 'september': 9, 'sept': 9,
    'oct': 10, 'october': 10,
    'nov': 11, 'november': 11,
    'dec': 12, 'december': 12
}

def parse_date_ranges_from_text(text: str) -> List[Tuple[int, int]]:
    """Universal date range extractor handling Month YYYY, MM/YYYY, and YYYY formats."""
    current_year = datetime.now().year
    current_month = datetime.now().month
    ranges = []

    # 1. Month-Name format: e.g., 'Jan 2024 - Dec 2024', 'January 2025 - May 2025', 'Oct 2024 - Present'
    month_pattern = re.compile(
        r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?,?\s*(\d{4})\s*[-–—to\s]+\s*(?:(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?,?\s*(\d{4})|[Pp]resent|[Cc]urrent)\b',
        re.IGNORECASE
    )

    for match in month_pattern.finditer(text):
        m1_str, y1_str = match.group(1).lower(), match.group(2)
        m2_str, y2_str = match.group(3), match.group(4)

        s_mo = MONTH_MAP.get(m1_str, 1)
        s_yr = int(y1_str)

        if m2_str and y2_str:
            e_mo = MONTH_MAP.get(m2_str.lower(), 12)
            e_yr = int(y2_str)
        else:
            e_mo = current_month
            e_yr = current_year

        if 1990 <= s_yr <= current_year and 1990 <= e_yr <= current_year + 1:
            start_m = s_yr * 12 + s_mo
            end_m = e_yr * 12 + e_mo
            if end_m >= start_m and (end_m - start_m) <= 480:
                ranges.append((start_m, end_m))

    # 2. MM/YYYY format: e.g., '01/2024 - 05/2024', '07/2024 – 12/2024'
    mmyyyy_pattern = re.compile(
        r'\b(0[1-9]|1[0-2])/(\d{4})\s*[-–—to\s]+\s*(?:(0[1-9]|1[0-2])/(\d{4})|[Pp]resent|[Cc]urrent)\b',
        re.IGNORECASE
    )

    for match in mmyyyy_pattern.finditer(text):
        s_mo = int(match.group(1))
        s_yr = int(match.group(2))
        if match.group(3) and match.group(4):
            e_mo = int(match.group(3))
            e_yr = int(match.group(4))
        else:
            e_mo = current_month
            e_yr = current_year

        if 1990 <= s_yr <= current_year and 1990 <= e_yr <= current_year + 1:
            start_m = s_yr * 12 + s_mo
            end_m = e_yr * 12 + e_mo
            if end_m >= start_m and (end_m - start_m) <= 480:
                ranges.append((start_m, end_m))

    # 3. YYYY - YYYY format: e.g., '2021 - 2024'
    yyyy_pattern = re.compile(
        r'\b(20\d{2}|19\d{2})\s*[-–—to\s]+\s*(20\d{2}|19\d{2}|[Pp]resent|[Cc]urrent)\b',
        re.IGNORECASE
    )

    for match in yyyy_pattern.finditer(text):
        s_yr = int(match.group(1))
        end_str = match.group(2)
        if re.match(r'pres|curr', end_str, re.IGNORECASE):
            e_yr = current_year
            e_mo = current_month
        else:
            e_yr = int(end_str)
            e_mo = 12

            # Academic degree timeline filter: 3-5 year span ending in current/future year (e.g., 2022-2026, 2023-2027) is a degree
            if e_yr >= current_year and (e_yr - s_yr) >= 3:
                continue

        s_mo = 1
        if 1990 <= s_yr <= current_year and 1990 <= e_yr <= current_year + 1:
            start_m = s_yr * 12 + s_mo
            end_m = e_yr * 12 + e_mo
            if end_m >= start_m and (end_m - start_m) <= 480:
                ranges.append((start_m, end_m))

    return ranges

def estimate_candidate_yoe(cv_text_or_sections) -> float:
    """
    Universal YOE extraction:
    1. Evaluates explicit professional experience statements in summary/full text.
    2. Focuses strictly on professional work experience lines (excluding academic projects and education).
    3. Recovers work role blocks mis-categorized under other sections.
    4. Parses multi-format date ranges, merges overlapping spans, and calculates total YOE.
    """
    full_text = ""
    sections = {}

    if isinstance(cv_text_or_sections, dict):
        sections = cv_text_or_sections
        full_text = " ".join([v for v in cv_text_or_sections.values() if v])
    else:
        full_text = str(cv_text_or_sections)

    # STEP 1: Check for explicit professional experience statements
    explicit_patterns = [
        r'(?:over|more than|\+)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:professional\s+)?(?:experience|exp)',
        r'(?:experience|exp)(?:\s+of)?\s+(?:over|more than|\+)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)'
    ]

    for pat in explicit_patterns:
        match = re.search(pat, full_text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                if 0.5 <= val < 40:
                    return val
            except ValueError:
                pass

    # STEP 2: Gather target text lines strictly from work experience (and mis-categorized work role blocks)
    exp = sections.get("experience", "")
    
    # Precise work role indicators (for recovering work roles mis-classified into skills/other)
    work_role_patterns = [
        r'\b(?:business development|software|backend|frontend|full stack|data|devops|cloud|ai|ml|lead|senior|junior)\s+(?:associate|engineer|developer|architect|consultant|analyst|specialist|manager|officer|executive)\b',
        r'\b(?:intern at|internship|full-time|part-time|employment)\b'
    ]

    extra_work_lines = []
    for sec_key in ["summary", "skills", "other"]:
        sec_text = sections.get(sec_key, "")
        if not sec_text:
            continue
        lines = sec_text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(re.search(pat, line_lower) for pat in work_role_patterns):
                start_i = max(0, i - 1)
                end_i = min(len(lines), i + 4)
                extra_work_lines.extend(lines[start_i:end_i])

    target_text = f"{exp}\n" + "\n".join(extra_work_lines)
    if not target_text.strip():
        target_text = full_text

    # STEP 3: Context-aware academic degree line filtering
    academic_keywords = [
        'bachelor', 'master', 'phd', 'degree', 'b.s', 'bs ', 'b.sc', 'm.s', 'm.sc',
        'gce a level', 'a level', 'high school', 'matric', 'fsc', 'education',
        'fast-nuces', 'comsats', 'nuces', 'university', 'college', 'coursework', 'thesis',
        'undergraduate', 'class of 20', 'ieee student', 'student branch', 'forman christian',
        'beaconhouse', 'school'
    ]

    lines = target_text.split('\n')
    filtered_lines = []

    for i, line in enumerate(lines):
        line_lower = line.lower()
        context = line_lower
        if i > 0:
            context += " " + lines[i-1].lower()
        if i < len(lines) - 1:
            context += " " + lines[i+1].lower()

        if not any(kw in context for kw in academic_keywords):
            filtered_lines.append(line)

    clean_work_text = "\n".join(filtered_lines)

    # STEP 4: Parse date ranges & merge overlapping periods
    parsed_ranges = parse_date_ranges_from_text(clean_work_text)

    if not parsed_ranges:
        return 0.0

    parsed_ranges.sort(key=lambda x: x[0])
    merged_ranges = [parsed_ranges[0]]

    for current_start, current_end in parsed_ranges[1:]:
        prev_start, prev_end = merged_ranges[-1]
        if current_start <= prev_end:
            merged_ranges[-1] = (prev_start, max(prev_end, current_end))
        else:
            merged_ranges.append((current_start, current_end))

    total_months = sum(end - start for start, end in merged_ranges)
    return round(total_months / 12.0, 1)


# =====================================================================
# MATRIX SCORING ENGINE
# =====================================================================

class HybridScorer:
    """
    Consolidated Matrix Scoring Engine.
    All scoring logic (semantic match, BM25, must-haves, YOE, recency) is
    evaluated inside score_candidates in a single pass.
    """

    def __init__(self, vector_model: Optional[SentenceTransformer] = None, model_name: str = "all-MiniLM-L6-v2"):
        if vector_model is not None:
            self.vector_model = vector_model
        else:
            self.vector_model = SentenceTransformer(model_name)

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'\w+', text.lower())

    def _compute_cosine_scores(self, anchor_text: str, target_texts: list[str]) -> list[float]:
        if not anchor_text.strip() or not target_texts:
            return [0.0] * len(target_texts)

        anchor_emb = self.vector_model.encode(anchor_text, convert_to_tensor=True)
        target_embs = self.vector_model.encode(target_texts, convert_to_tensor=True)
        similarities = util.cos_sim(anchor_emb, target_embs)[0].tolist()
        return [max(0.0, float(s)) for s in similarities]

    def _compute_bm25_scores(self, query_text: str, corpus_texts: list[str]) -> list[float]:
        tokenized_corpus = [self._tokenize(t) for t in corpus_texts]
        tokenized_query = self._tokenize(query_text)

        if not tokenized_query:
            return [0.0] * len(corpus_texts)

        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(tokenized_query)

        max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0
        return [min(1.0, float(s / max_score)) if max_score > 0 else 0.0 for s in scores]

    def _split_experience_for_recency(self, experience_text: str) -> tuple:
        if not experience_text.strip():
            return ("", "")

        lines = [l for l in experience_text.split('\n') if l.strip()]
        if len(lines) <= 3:
            return (experience_text, "")

        midpoint = len(lines) // 2
        recent = "\n".join(lines[:midpoint])
        older = "\n".join(lines[midpoint:])
        return (recent, older)

    def _calibrate_scores(self, raw_scores: list[float]) -> list[float]:
        calibrated = []
        ANCHOR_MIN = 0.10  # Theoretical floor
        ANCHOR_MAX = 0.75  # Theoretical ceiling
        RANGE = ANCHOR_MAX - ANCHOR_MIN

        for s in raw_scores:
            normalized = (s - ANCHOR_MIN) / RANGE if RANGE > 0 else 0.0
            pct = max(0.0, min(100.0, normalized * 100.0))
            calibrated.append(round(pct, 2))

        return calibrated

    def score_candidates(
        self,
        jd_text: str,
        candidates: list[dict],
        must_have_skills: list[str] = None,
        nice_to_have_skills: list[str] = None,
        target_yoe: float = 0.0,
        vector_weight: float = 0.6,
        bm25_weight: float = 0.4,
        penalty_severity: float = 0.15
    ) -> list[dict]:
        """
        Consolidated Matrix Scoring Pipeline with full audit trail.
        Evaluates semantic similarity, BM25, must-have skills, recency, and YOE.
        Returns fully-computed results with transparent audit breakdown.

        Args:
            penalty_severity: Maximum fraction of score deducted for missing ALL
                must-have skills. Range 0.0 (no penalty) to 0.50 (harsh penalty).
                Default 0.15 means missing ALL skills costs at most 15%.
            nice_to_have_skills: Optional bonus skills — matching these adds a
                small boost without penalizing candidates who lack them.
        """
        if must_have_skills is None:
            must_have_skills = []
        if nice_to_have_skills is None:
            nice_to_have_skills = []

        if not candidates:
            return []

        n = len(candidates)

        # --- EXTRACT SECTION TEXTS ---
        cv_skills_texts = []
        cv_recent_exp_texts = []
        cv_older_exp_texts = []

        for c in candidates:
            sections = c.get("sections", {})
            skills = sections.get("skills", "")
            experience = sections.get("experience", "")
            full = c.get("full_text", "")

            cv_skills_texts.append(skills if skills.strip() else full)

            exp_source = experience if experience.strip() else full
            recent, older = self._split_experience_for_recency(exp_source)
            cv_recent_exp_texts.append(recent if recent.strip() else exp_source)
            cv_older_exp_texts.append(older if older.strip() else "")

        # --- SECTION-TARGETED SEMANTIC SCORING ---
        skills_cosine = self._compute_cosine_scores(jd_text, cv_skills_texts)
        recent_exp_cosine = self._compute_cosine_scores(jd_text, cv_recent_exp_texts)

        has_older = any(t.strip() for t in cv_older_exp_texts)
        if has_older:
            older_exp_cosine = self._compute_cosine_scores(jd_text, cv_older_exp_texts)
        else:
            older_exp_cosine = [0.0] * n

        vector_scores = []
        for i in range(n):
            weighted = (
                skills_cosine[i] * 0.35 +
                recent_exp_cosine[i] * 0.45 +
                older_exp_cosine[i] * 0.20
            )
            vector_scores.append(weighted)

        # --- BM25 KEYWORD SCORING ---
        bm25_corpus = [f"{cv_skills_texts[i]} {cv_recent_exp_texts[i]}" for i in range(n)]
        bm25_scores = self._compute_bm25_scores(jd_text, bm25_corpus)

        # --- COMBINE VECTOR + BM25 ---
        raw_composite = []
        for i in range(n):
            composite = (vector_scores[i] * vector_weight) + (bm25_scores[i] * bm25_weight)
            raw_composite.append(composite)

        # --- ANCHORED CALIBRATION ---
        calibrated_scores = self._calibrate_scores(raw_composite)

        # --- MUST-HAVE SKILL EVALUATION & CONFIGURABLE PENALTY ---
        must_have_results = []
        skill_penalty_pcts = []
        for i, c in enumerate(candidates):
            sections = c.get("sections", {})
            eval_result = evaluate_skill_context(sections, must_have_skills)
            must_have_results.append(eval_result)

            pre_penalty_score = calibrated_scores[i]
            if must_have_skills:
                coverage = eval_result["ratio"]
                # penalty_severity controls max deduction: e.g. 0.15 means at most -15%
                penalty_multiplier = (1.0 - penalty_severity) + (penalty_severity * coverage)
                calibrated_scores[i] = round(calibrated_scores[i] * penalty_multiplier, 2)

            skill_penalty_pcts.append(round(calibrated_scores[i] - pre_penalty_score, 2))

        # --- NICE-TO-HAVE BONUS ---
        nice_to_have_results = []
        bonus_pcts = []
        for i, c in enumerate(candidates):
            if nice_to_have_skills:
                sections = c.get("sections", {})
                eval_bonus = evaluate_skill_context(sections, nice_to_have_skills)
                nice_to_have_results.append(eval_bonus)
                # Max +5% bonus for matching all nice-to-haves
                bonus = round(calibrated_scores[i] * 0.05 * eval_bonus["ratio"], 2)
                calibrated_scores[i] = round(min(99.0, calibrated_scores[i] + bonus), 2)
                bonus_pcts.append(bonus)
            else:
                nice_to_have_results.append({"contextual": [], "stuffed": [], "missing": [], "ratio": 0.0})
                bonus_pcts.append(0.0)

        # --- YOE EXTRACTION & MODIFIER ---
        candidate_yoes = []
        yoe_modifier_pcts = []
        for i, c in enumerate(candidates):
            sections = c.get("sections", {})
            yoe = estimate_candidate_yoe(sections if sections else c.get("full_text", ""))
            candidate_yoes.append(yoe)

            pre_yoe_score = calibrated_scores[i]
            if target_yoe > 0.0:
                if yoe >= target_yoe:
                    calibrated_scores[i] = round(min(99.0, calibrated_scores[i] * 1.05), 2)
                elif 0 < yoe < target_yoe:
                    calibrated_scores[i] = round(calibrated_scores[i] * 0.96, 2)

            yoe_modifier_pcts.append(round(calibrated_scores[i] - pre_yoe_score, 2))

        # --- BUILD RESULTS WITH FULL AUDIT TRAIL ---
        results = []
        for i, c in enumerate(candidates):
            
            # Raw point sub-scores (out of their maximum weight)
            skill_match_pts = round(skills_cosine[i] * 35, 1)
            recent_exp_pts = round(recent_exp_cosine[i] * 45, 1)
            older_exp_pts = round(older_exp_cosine[i] * 20, 1)
            bm25_pts = round(bm25_scores[i] * 100, 1)
            
            all_matched_must_haves = must_have_results[i]["contextual"] + must_have_results[i]["stuffed"]
            all_matched_nice = nice_to_have_results[i]["contextual"] + nice_to_have_results[i]["stuffed"]

            results.append({
                "file_name": c["file_name"],
                "final_score_pct": calibrated_scores[i],
                "vector_score_pct": round(vector_scores[i] * 100, 2),
                "bm25_score_pct": round(bm25_scores[i] * 100, 2),
                "matched_skills": all_matched_must_haves,  # backward compatibility
                "contextual_skills": must_have_results[i]["contextual"],
                "stuffed_skills": must_have_results[i]["stuffed"],
                "missing_skills": must_have_results[i]["missing"],
                "nice_to_have_matched": all_matched_nice,
                "candidate_yoe": candidate_yoes[i],
                "sections": c.get("sections", {}),
                "audit": {
                    "subscores": {
                        "skill_match": skill_match_pts,
                        "recent_exp": recent_exp_pts,
                        "older_exp": older_exp_pts,
                        "bm25_keyword": bm25_pts
                    },
                    "skills_similarity_pct": round(skills_cosine[i] * 100, 2),
                    "recent_exp_similarity_pct": round(recent_exp_cosine[i] * 100, 2),
                    "older_exp_similarity_pct": round(older_exp_cosine[i] * 100, 2),
                    "raw_vector_pct": round(vector_scores[i] * 100, 2),
                    "raw_bm25_pct": round(bm25_scores[i] * 100, 2),
                    "composite_base_pct": round(self._calibrate_scores([raw_composite[i]])[0], 2),
                    "must_have_penalty_pct": skill_penalty_pcts[i],
                    "nice_to_have_bonus_pct": bonus_pcts[i],
                    "yoe_modifier_pct": yoe_modifier_pcts[i],
                    "calibrated_final_pct": calibrated_scores[i]
                }
            })

        return sorted(results, key=lambda x: x["final_score_pct"], reverse=True)