"""
Educational Outcomes Analysis for Phase 5 (Step 5.5).

Quantitative analysis:
- Paired Wilcoxon tests: AI vs. instructor feedback quality improvement
- Cliff's delta effect size
- ANCOVA with pre-test scores as covariate
- SUS scoring (0–100 scale)
- TAM analysis: Cronbach's alpha, PU and PEU means with CIs
- Normalized learning gain

Qualitative analysis support:
- Thematic coding framework
- Inter-coder reliability
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class SUSResult:
    """System Usability Scale result."""

    raw_responses: list[list[int]]  # Each inner list = 10 responses from one participant
    n_participants: int
    mean_score: float
    std_score: float
    ci_95: tuple[float, float]
    interpretation: str  # below average, average, good, excellent


@dataclass
class TAMResult:
    """Technology Acceptance Model result."""

    pu_scores: list[float]  # Per-participant PU mean
    peu_scores: list[float]  # Per-participant PEU mean
    pu_mean: float
    pu_ci_95: tuple[float, float]
    peu_mean: float
    peu_ci_95: tuple[float, float]
    pu_cronbach_alpha: float
    peu_cronbach_alpha: float


@dataclass
class LearningGainResult:
    """Normalized learning gain comparison."""

    n: int
    ai_gains: list[float]
    instructor_gains: list[float]
    ai_mean_gain: float
    instructor_mean_gain: float
    wilcoxon_w: float
    p_value: float
    cliffs_delta: float
    cliffs_interpretation: str


def compute_sus(responses: list[list[int]]) -> SUSResult:
    """Compute SUS scores from raw responses.

    SUS scoring (Brooke, 1996):
    - Odd items (1,3,5,7,9): score = response - 1
    - Even items (2,4,6,8,10): score = 5 - response
    - Sum × 2.5 = score on 0–100 scale

    Args:
        responses: List of participant responses. Each inner list contains
            10 integers (1–5 Likert) in SUS item order.

    Returns:
        SUSResult with computed SUS scores.
    """
    scores = []
    for resp in responses:
        if len(resp) != 10:
            continue
        adjusted = []
        for i, val in enumerate(resp):
            if i % 2 == 0:  # Odd items (0-indexed: 0,2,4,6,8)
                adjusted.append(val - 1)
            else:  # Even items (0-indexed: 1,3,5,7,9)
                adjusted.append(5 - val)
        scores.append(sum(adjusted) * 2.5)

    scores = np.array(scores)
    n = len(scores)
    mean_score = float(scores.mean()) if n > 0 else 0
    std_score = float(scores.std(ddof=1)) if n > 1 else 0

    # 95% CI
    if n > 1:
        se = std_score / np.sqrt(n)
        t_crit = stats.t.ppf(0.975, n - 1)
        ci = (mean_score - t_crit * se, mean_score + t_crit * se)
    else:
        ci = (mean_score, mean_score)

    # Interpretation
    if mean_score >= 85:
        interp = "excellent"
    elif mean_score >= 80:
        interp = "good"
    elif mean_score >= 68:
        interp = "above average"
    elif mean_score >= 50:
        interp = "below average"
    else:
        interp = "poor"

    return SUSResult(
        raw_responses=responses,
        n_participants=n,
        mean_score=round(mean_score, 2),
        std_score=round(std_score, 2),
        ci_95=(round(ci[0], 2), round(ci[1], 2)),
        interpretation=interp,
    )


def cronbach_alpha(items: np.ndarray) -> float:
    """Compute Cronbach's alpha for internal consistency.

    Args:
        items: Array of shape (n_participants, n_items).

    Returns:
        Cronbach's alpha value. Target ≥ 0.7.
    """
    n_items = items.shape[1]
    if n_items < 2:
        return 0.0

    item_variances = items.var(axis=0, ddof=1)
    total_variance = items.sum(axis=1).var(ddof=1)

    if total_variance == 0:
        return 0.0

    return (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)


def compute_tam(
    pu_items: list[list[int]],
    peu_items: list[list[int]],
) -> TAMResult:
    """Compute TAM analysis results.

    Args:
        pu_items: List of participant responses for PU items.
            Each inner list contains 6 integers (1–7 Likert).
        peu_items: List of participant responses for PEU items.
            Each inner list contains 6 integers (1–7 Likert).

    Returns:
        TAMResult with means, CIs, and Cronbach's alpha.
    """
    pu_array = np.array(pu_items, dtype=float)
    peu_array = np.array(peu_items, dtype=float)

    pu_means = pu_array.mean(axis=1)
    peu_means = peu_array.mean(axis=1)
    n = len(pu_means)

    def _ci(data):
        if len(data) < 2:
            return (float(data.mean()), float(data.mean()))
        se = data.std(ddof=1) / np.sqrt(len(data))
        t_crit = stats.t.ppf(0.975, len(data) - 1)
        m = data.mean()
        return (round(float(m - t_crit * se), 2), round(float(m + t_crit * se), 2))

    return TAMResult(
        pu_scores=pu_means.tolist(),
        peu_scores=peu_means.tolist(),
        pu_mean=round(float(pu_means.mean()), 2),
        pu_ci_95=_ci(pu_means),
        peu_mean=round(float(peu_means.mean()), 2),
        peu_ci_95=_ci(peu_means),
        pu_cronbach_alpha=round(cronbach_alpha(pu_array), 4),
        peu_cronbach_alpha=round(cronbach_alpha(peu_array), 4),
    )


def normalized_gain(pre: float, post: float, max_score: float = 4.0) -> float:
    """Compute normalized learning gain.

    Formula: (post - pre) / (max - pre)

    Args:
        pre: Pre-test score.
        post: Post-test score.
        max_score: Maximum possible score.

    Returns:
        Normalized gain (0–1 range, can be negative for regression).
    """
    if max_score - pre == 0:
        return 0.0
    return (post - pre) / (max_score - pre)


def compare_feedback_conditions(
    ai_pre: list[float],
    ai_post: list[float],
    instructor_pre: list[float],
    instructor_post: list[float],
    max_score: float = 4.0,
) -> LearningGainResult:
    """Compare learning gains between AI and instructor feedback conditions.

    Uses paired Wilcoxon test (within-subjects design) and Cliff's delta.

    Args:
        ai_pre: Pre-test scores under AI feedback condition.
        ai_post: Post-test scores under AI feedback condition.
        instructor_pre: Pre-test scores under instructor feedback condition.
        instructor_post: Post-test scores under instructor feedback condition.
        max_score: Maximum possible score.

    Returns:
        LearningGainResult with comparison statistics.
    """
    ai_gains = [
        normalized_gain(pre, post, max_score)
        for pre, post in zip(ai_pre, ai_post)
    ]
    instructor_gains = [
        normalized_gain(pre, post, max_score)
        for pre, post in zip(instructor_pre, instructor_post)
    ]

    ai_arr = np.array(ai_gains)
    inst_arr = np.array(instructor_gains)
    n = len(ai_arr)

    # Wilcoxon signed-rank test
    try:
        w_stat, p_val = stats.wilcoxon(ai_arr, inst_arr)
    except ValueError:
        w_stat, p_val = 0.0, 1.0

    # Cliff's delta
    from adr_analyser.evaluation.comparison import compute_cliffs_delta

    cd = compute_cliffs_delta(ai_arr, inst_arr)

    return LearningGainResult(
        n=n,
        ai_gains=ai_gains,
        instructor_gains=instructor_gains,
        ai_mean_gain=round(float(ai_arr.mean()), 4),
        instructor_mean_gain=round(float(inst_arr.mean()), 4),
        wilcoxon_w=round(float(w_stat), 4),
        p_value=round(float(p_val), 6),
        cliffs_delta=cd.delta,
        cliffs_interpretation=cd.interpretation,
    )


# Thematic coding framework for qualitative analysis
THEMATIC_CODING_FRAMEWORK = {
    "positive_themes": [
        {"code": "P-HELP", "description": "Feedback was helpful for specific improvements"},
        {"code": "P-SPEC", "description": "Feedback was specific and actionable"},
        {"code": "P-TIME", "description": "Timeliness / immediacy of feedback valued"},
        {"code": "P-COMP", "description": "Comprehensive coverage of multiple dimensions"},
        {"code": "P-LEARN", "description": "Contributed to learning about ADR quality"},
        {"code": "P-FAIR", "description": "Perceived as fair and objective"},
    ],
    "negative_themes": [
        {"code": "N-HALL", "description": "Hallucinations or factual errors in feedback"},
        {"code": "N-GENERIC", "description": "Feedback too generic / not specific enough"},
        {"code": "N-OVER", "description": "Concern about over-reliance on AI"},
        {"code": "N-TRUST", "description": "Low trust in AI assessment accuracy"},
        {"code": "N-CONTEXT", "description": "AI lacked project/course context"},
        {"code": "N-RIGID", "description": "Scoring felt too rigid or formulaic"},
    ],
    "comparative_themes": [
        {"code": "C-TRUST", "description": "Trust comparison between AI and instructor"},
        {"code": "C-PREF", "description": "Overall preference (AI vs. instructor)"},
        {"code": "C-EMOT", "description": "Emotional response to AI vs. human feedback"},
        {"code": "C-DEPTH", "description": "Depth comparison between feedback types"},
        {"code": "C-COMPL", "description": "Complementary use of both feedback types"},
    ],
}
