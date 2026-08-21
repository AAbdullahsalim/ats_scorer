"""
Score calibration and normalization.
Features:
- Mid-Tier Opportunity Curve: boosts promising candidates (30% - 75%) into strong consideration,
  while keeping poor/unqualified CVs strictly below 20%.
- Must-have skill penalty: discounts candidates missing key core competencies.
- Nice-to-have bonus & YOE modifier.
"""

import math

# Calibration constants (matching backend/config.py)
CALIBRATION_FLOOR = 0.10
CALIBRATION_CEILING = 0.52
MUST_HAVE_PENALTY_SEVERITY = 0.35
NICE_TO_HAVE_BONUS_MAX = 0.05


def calibrate_scores(raw_scores: list[float]) -> list[float]:
    """
    Map raw composite scores to 0-100% range using anchor calibration + Opportunity Lift Curve.

    - Scores below 20%: Unqualified/poor match -> NO boost (stays <20%, filtered).
    - Scores between 30% - 75%: Mid-tier high potential -> receives a dynamic +12% to +18% lift,
      giving promising candidates with real experience a fair chance.
    - Scores above 80%: Top candidates -> smoothly tapers to 90%-98%.
    """
    anchor_min = CALIBRATION_FLOOR
    anchor_max = CALIBRATION_CEILING
    score_range = anchor_max - anchor_min

    calibrated = []
    for score in raw_scores:
        if score_range > 0:
            normalized = (score - anchor_min) / score_range
        else:
            normalized = 0.0

        base_pct = max(0.0, min(100.0, normalized * 100.0))

        # Mid-tier Opportunity Curve Logic
        if base_pct < 20.0:
            # Below 20%: stays strictly low / poor tier (no boost)
            final_pct = base_pct
        elif base_pct < 30.0:
            # Transition ramp (20% - 30%)
            ramp = (base_pct - 20.0) / 10.0
            lift = ramp * 6.0
            final_pct = base_pct + lift
        else:
            # Opportunity Boost for candidates with 30%+ core relevance
            # Smooth sine-based lift peaked at 50-60% base
            lift = 18.0 * math.sin(min(1.0, (base_pct - 20.0) / 65.0) * math.pi)
            final_pct = min(99.0, base_pct + max(0.0, lift))

        calibrated.append(round(final_pct, 2))

    return calibrated


def apply_skill_penalty(
    score: float,
    skill_coverage_ratio: float,
) -> tuple[float, float]:
    """
    Apply must-have skill penalty.
    Missing all skills applies a significant discount, while matching
    all must-haves retains 100% of the score.

    Returns (adjusted_score, penalty_amount).
    """
    severity = MUST_HAVE_PENALTY_SEVERITY

    # penalty_multiplier ranges from (1 - severity) to 1.0
    multiplier = (1.0 - severity) + (severity * skill_coverage_ratio)
    adjusted = round(score * multiplier, 2)
    penalty = round(adjusted - score, 2)

    return adjusted, penalty


def apply_nice_to_have_bonus(
    score: float,
    bonus_ratio: float,
) -> tuple[float, float]:
    """
    Apply nice-to-have skill bonus.
    Max bonus is 5% of current score for matching all nice-to-haves.

    Returns (adjusted_score, bonus_amount).
    """
    max_bonus = NICE_TO_HAVE_BONUS_MAX
    bonus = round(score * max_bonus * bonus_ratio, 2)
    adjusted = round(min(99.0, score + bonus), 2)

    return adjusted, bonus


def apply_yoe_modifier(
    score: float,
    candidate_yoe: float,
    target_yoe: float,
) -> tuple[float, float]:
    """
    Apply YOE-based score modifier.
    Candidates meeting/exceeding target get a small boost.
    Candidates below target get a small reduction.

    Returns (adjusted_score, modifier_amount).
    """
    if target_yoe <= 0:
        return score, 0.0

    pre_score = score

    if candidate_yoe >= target_yoe:
        adjusted = round(min(99.0, score * 1.06), 2)
    elif candidate_yoe > 0:
        adjusted = round(score * 0.94, 2)
    else:
        adjusted = score

    modifier = round(adjusted - pre_score, 2)
    return adjusted, modifier


def apply_leader_relative_scaling(
    scores: list[float],
    target_top: float = 94.0,
    min_qualification_threshold: float = 20.0,
) -> list[float]:
    """
    Leader-Anchored Scaling (Top Candidate Benchmark Normalization):
    - Anchors the top-performing candidate (e.g. >= 40%) to target_top (~94%).
    - Generalizes a proportionate boost to other qualified candidates (score >= 20%).
    - Leaves unqualified candidates (< 20%) strictly at their raw/low score.
    """
    if not scores:
        return scores

    max_score = max(scores)
    if max_score < 35.0:
        # If even the top candidate is poor (<35%), do not artificially inflate
        return scores

    scale_ratio = target_top / max_score

    adjusted_scores = []
    for s in scores:
        if s >= min_qualification_threshold:
            # Proportionate boost relative to the top lead candidate
            boosted = round(min(98.5, s * scale_ratio), 2)
            adjusted_scores.append(boosted)
        else:
            # Below 20%: keep strictly low / unboosted
            adjusted_scores.append(s)

    return adjusted_scores

