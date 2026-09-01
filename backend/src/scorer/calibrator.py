"""
Score calibration and normalization.
Features:
- Fixed Calibration Curve: independent of batch size.
- Must-have skill penalty: discounts candidates missing key core competencies.
- Nice-to-have bonus & YOE modifier.

v2: Removed unstable leader-anchored scaling. Made 40%+ scores slightly less strict.
Importing constants from config.py as single source of truth.
"""

import math
from config import (
    CALIBRATION_FLOOR,
    CALIBRATION_CEILING,
    MUST_HAVE_PENALTY_SEVERITY,
    NICE_TO_HAVE_BONUS_MAX
)


def calibrate_scores(raw_scores: list[float]) -> list[float]:
    """
    Map raw composite scores to 0-100% range using a FIXED calibration curve.
    This guarantees that adding/removing a CV does not shift other CVs' scores.
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

        # FIXED CALIBRATION CURVE
        # Raw 0-20%: Stays low (unqualified)
        # Raw 20-40%: Weak match, small boost
        # Raw 40%+: Decent/Strong match, smoothed boost (less strict as requested)
        if base_pct < 20.0:
            final_pct = base_pct
        elif base_pct < 40.0:
            ramp = (base_pct - 20.0) / 20.0
            lift = ramp * 15.0  # +15% boost max at 40
            final_pct = base_pct + lift
        else:
            # For 40%+, we apply a more generous sine curve to make it less strict
            # It boosts 40% -> ~60%, 60% -> ~80%, 80% -> ~95%
            lift = 25.0 * math.sin(min(1.0, (base_pct - 20.0) / 80.0) * math.pi)
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
