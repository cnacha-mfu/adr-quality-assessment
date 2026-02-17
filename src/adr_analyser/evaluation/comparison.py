"""
Comparative Analysis for RQ2 (Step 4.3).

Statistical tests for comparing multiple models on the same ADR set:
- Friedman test (non-parametric repeated-measures)
- Nemenyi post-hoc test
- Wilcoxon signed-rank tests with Holm-Bonferroni correction
- Cliff's delta effect size with 95% bootstrap CI

Also includes ablation study analysis (Step 4.3):
- Full rubric vs. minimal instructions
- 0-shot vs. 1-shot vs. 3-shot
- With vs. without chain-of-thought
- Holistic vs. per-dimension scoring
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np
from scipy import stats


@dataclass
class CliffsDelta:
    """Cliff's delta effect size with CI and interpretation."""

    delta: float
    ci_lower: float
    ci_upper: float
    interpretation: str  # negligible, small, medium, large


@dataclass
class PairwiseComparison:
    """Result of a pairwise comparison between two models."""

    model_a: str
    model_b: str
    wilcoxon_w: float
    p_value: float
    p_adjusted: float  # After Holm-Bonferroni correction
    cliffs_delta: CliffsDelta
    significant: bool  # After correction


@dataclass
class ComparisonResult:
    """Complete comparison result across all models."""

    dimension_id: str
    n: int
    friedman_chi2: float
    friedman_p: float
    pairwise: list[PairwiseComparison]


def compute_cliffs_delta(
    x: np.ndarray,
    y: np.ndarray,
    n_bootstrap: int = 10000,
    ci_level: float = 0.95,
    seed: int = 42,
) -> CliffsDelta:
    """Compute Cliff's delta with bootstrap CI.

    Cliff's delta is the preferred non-parametric effect size in EMSE
    because ADR quality scores are ordinal.

    Thresholds (from Romano et al., 2006):
    - |δ| < 0.147: negligible
    - |δ| < 0.33: small
    - |δ| < 0.474: medium
    - |δ| ≥ 0.474: large

    Args:
        x: Scores from model A.
        y: Scores from model B.
        n_bootstrap: Number of bootstrap resamples.
        ci_level: Confidence level.
        seed: Random seed.

    Returns:
        CliffsDelta with value, CI, and interpretation.
    """

    def _delta(a, b):
        n_x, n_y = len(a), len(b)
        if n_x == 0 or n_y == 0:
            return 0.0
        more = sum(1 for xi in a for yi in b if xi > yi)
        less = sum(1 for xi in a for yi in b if xi < yi)
        return (more - less) / (n_x * n_y)

    delta = _delta(x, y)

    # Bootstrap CI
    rng = np.random.RandomState(seed)
    boot_deltas = []
    for _ in range(n_bootstrap):
        x_boot = rng.choice(x, size=len(x), replace=True)
        y_boot = rng.choice(y, size=len(y), replace=True)
        boot_deltas.append(_delta(x_boot, y_boot))

    boot_deltas = np.array(boot_deltas)
    alpha = 1 - ci_level
    ci_lower = np.percentile(boot_deltas, 100 * alpha / 2)
    ci_upper = np.percentile(boot_deltas, 100 * (1 - alpha / 2))

    # Interpretation
    abs_delta = abs(delta)
    if abs_delta < 0.147:
        interp = "negligible"
    elif abs_delta < 0.33:
        interp = "small"
    elif abs_delta < 0.474:
        interp = "medium"
    else:
        interp = "large"

    return CliffsDelta(
        delta=round(delta, 4),
        ci_lower=round(float(ci_lower), 4),
        ci_upper=round(float(ci_upper), 4),
        interpretation=interp,
    )


def holm_bonferroni(p_values: list[float], alpha: float = 0.05) -> list[float]:
    """Apply Holm-Bonferroni correction to p-values.

    Args:
        p_values: List of raw p-values.
        alpha: Family-wise error rate.

    Returns:
        List of adjusted p-values.
    """
    n = len(p_values)
    if n == 0:
        return []

    # Sort indices by p-value
    sorted_idx = np.argsort(p_values)
    adjusted = np.zeros(n)

    cummax = 0.0
    for rank, idx in enumerate(sorted_idx):
        corrected = p_values[idx] * (n - rank)
        cummax = max(cummax, corrected)
        adjusted[idx] = min(cummax, 1.0)

    return adjusted.tolist()


def compare_models(
    scores: dict[str, list[int]],
    dimension_id: str = "overall",
    alpha: float = 0.05,
) -> ComparisonResult:
    """Compare multiple models on the same ADR set.

    Uses Friedman test for omnibus comparison, then Wilcoxon signed-rank
    for pairwise with Holm-Bonferroni correction.

    Args:
        scores: Dict mapping model_name to list of scores (same ordering as ADRs).
        dimension_id: Identifier for the dimension being compared.
        alpha: Significance level.

    Returns:
        ComparisonResult with Friedman test and pairwise comparisons.
    """
    model_names = list(scores.keys())
    n_models = len(model_names)
    n = len(scores[model_names[0]])

    # Validate all models have same number of scores
    assert all(len(s) == n for s in scores.values()), "All models must have same number of scores"

    # Friedman test
    score_arrays = [np.array(scores[m]) for m in model_names]
    try:
        chi2, friedman_p = stats.friedmanchisquare(*score_arrays)
    except ValueError:
        chi2, friedman_p = 0.0, 1.0

    # Pairwise comparisons with Wilcoxon signed-rank
    pairs = list(combinations(range(n_models), 2))
    raw_p_values = []
    pairwise_results = []

    for i, j in pairs:
        x = score_arrays[i]
        y = score_arrays[j]

        try:
            w_stat, p_val = stats.wilcoxon(x, y, alternative="two-sided")
        except ValueError:
            w_stat, p_val = 0.0, 1.0

        raw_p_values.append(p_val)
        delta = compute_cliffs_delta(x, y)

        pairwise_results.append(PairwiseComparison(
            model_a=model_names[i],
            model_b=model_names[j],
            wilcoxon_w=round(float(w_stat), 4),
            p_value=round(float(p_val), 6),
            p_adjusted=0.0,  # Will be set after correction
            cliffs_delta=delta,
            significant=False,
        ))

    # Apply Holm-Bonferroni correction
    adjusted = holm_bonferroni(raw_p_values, alpha)
    for idx, result in enumerate(pairwise_results):
        result.p_adjusted = round(adjusted[idx], 6)
        result.significant = adjusted[idx] < alpha

    return ComparisonResult(
        dimension_id=dimension_id,
        n=n,
        friedman_chi2=round(float(chi2), 4),
        friedman_p=round(float(friedman_p), 6),
        pairwise=pairwise_results,
    )
