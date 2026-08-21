"""
Score calibration and normalization.
Fixes Bug #6: calibration anchors too tight, compressing good scores.

Changes from v1:
- Lowered ANCHOR_MIN from 0.10 to 0.08
- Lowered ANCHOR_MAX from 0.75 to 0.60 (realistic ceiling for MiniLM CV-to-JD)
- Must-have penalty is now visual-only (minimal score impact)
- Nice-to-have bonus preserved
"""

# Calibration constants (matching backend/config.py)
CALIBRATION_FLOOR = 0.08
CALIBRATION_CEILING = 0.60
MUST_HAVE_PENALTY_SEVERITY = 0.08
NICE_TO_HAVE_BONUS_MAX = 0.05


def calibrate_scores(raw_scores: list[float]) -> list[float]:
    """
    Map raw composite scores to 0-100% range using anchor calibration.

    The anchor points define the expected range of raw scores from
    the hybrid vector+BM25 scoring. Scores below the floor map to ~0%,
    scores above the ceiling map to ~100%.
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

        pct = max(0.0, min(100.0, normalized * 100.0))
        calibrated.append(round(pct, 2))

    return calibrated


def apply_skill_penalty(
    score: float,
    skill_coverage_ratio: float,
) -> tuple[float, float]:
    """
    Apply must-have skill penalty.
    Penalty is intentionally LOW — missing skills are shown visually in the UI,
    not crushed numerically. A candidate missing 1-2 skills should still rank
    well if their overall profile is strong.

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
        adjusted = round(min(99.0, score * 1.05), 2)
    elif candidate_yoe > 0:
        adjusted = round(score * 0.96, 2)
    else:
        adjusted = score

    modifier = round(adjusted - pre_score, 2)
    return adjusted, modifier
