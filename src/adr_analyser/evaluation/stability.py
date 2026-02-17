"""
Stability Analysis for RQ3 (Steps 4.4–4.5).

Analyzes LLM assessment stability across:
- Multiple inference passes (intra-LLM ICC)
- Prompt variations (prompt sensitivity)
- Student cohorts (cross-cohort generalizability)

With 5 runs per ADR already collected, computes:
- Intra-LLM ICC(3,k) across runs (target > 0.90)
- Mean within-ADR standard deviation
- Percentage of ADRs with identical scores across all runs
- Maximum observed within-ADR range
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats

from adr_analyser.evaluation.agreement import compute_icc_21


@dataclass
class StabilityMetrics:
    """Stability metrics for a single dimension across multiple passes."""

    dimension_id: str
    n_adrs: int
    n_passes: int
    icc_3k: float  # ICC(3,k) consistency
    icc_3k_ci: tuple[float, float]
    mean_within_std: float  # Mean within-ADR standard deviation
    pct_identical: float  # % of ADRs with identical scores across all passes
    max_range: int  # Maximum observed within-ADR range
    mean_range: float  # Mean within-ADR range


def compute_icc_3k(
    ratings: np.ndarray,
    n_bootstrap: int = 10000,
    seed: int = 42,
) -> tuple[float, tuple[float, float]]:
    """Compute ICC(3,k) for consistency (two-way mixed, average measures).

    ICC(3,k) is appropriate when the same 'raters' (inference passes) are used
    for all subjects (ADRs), and we care about consistency rather than
    absolute agreement.

    Args:
        ratings: Array of shape (n_subjects, k_passes).
        n_bootstrap: Number of bootstrap resamples.
        seed: Random seed.

    Returns:
        Tuple of (ICC value, (lower_CI, upper_CI)).
    """
    n, k = ratings.shape
    if n < 2 or k < 2:
        return 0.0, (0.0, 0.0)

    def _icc_3k(data):
        n, k = data.shape
        grand_mean = data.mean()
        row_means = data.mean(axis=1)

        ss_rows = k * ((row_means - grand_mean) ** 2).sum()
        ss_total = ((data - grand_mean) ** 2).sum()
        ss_error = ss_total - ss_rows - k * ((data.mean(axis=0) - grand_mean) ** 2).sum()

        ms_rows = ss_rows / (n - 1) if n > 1 else 0
        ms_error = ss_error / ((n - 1) * (k - 1)) if (n > 1 and k > 1) else 0

        if ms_rows == 0:
            return 0.0
        return (ms_rows - ms_error) / ms_rows

    icc = _icc_3k(ratings)

    # Bootstrap CI
    rng = np.random.RandomState(seed)
    boot_vals = []
    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, size=n)
        boot_vals.append(_icc_3k(ratings[idx, :]))

    boot_vals = np.array(boot_vals)
    ci_lower = np.percentile(boot_vals, 2.5)
    ci_upper = np.percentile(boot_vals, 97.5)

    return round(float(icc), 4), (round(float(ci_lower), 4), round(float(ci_upper), 4))


def compute_stability(
    multi_pass_scores: dict[str, list[list[int]]],
    dimension_id: str = "overall",
) -> StabilityMetrics:
    """Compute stability metrics for multi-pass scoring.

    Args:
        multi_pass_scores: Dict mapping adr_filename to list of scores per pass.
            Each inner list has one score per pass.
            Example: {"adr1.md": [3, 3, 3, 2, 3], "adr2.md": [1, 1, 2, 1, 1]}
        dimension_id: Dimension identifier.

    Returns:
        StabilityMetrics with all computed statistics.
    """
    filenames = list(multi_pass_scores.keys())
    n_adrs = len(filenames)
    n_passes = len(next(iter(multi_pass_scores.values()))) if n_adrs > 0 else 0

    if n_adrs == 0 or n_passes < 2:
        return StabilityMetrics(
            dimension_id=dimension_id, n_adrs=n_adrs, n_passes=n_passes,
            icc_3k=0, icc_3k_ci=(0, 0), mean_within_std=0,
            pct_identical=0, max_range=0, mean_range=0,
        )

    # Build ratings matrix (n_adrs × n_passes)
    ratings = np.array([multi_pass_scores[f] for f in filenames], dtype=float)

    # ICC(3,k)
    icc, icc_ci = compute_icc_3k(ratings)

    # Within-ADR statistics
    within_stds = ratings.std(axis=1, ddof=1)
    mean_within_std = float(within_stds.mean())

    # Percentage with identical scores
    ranges = ratings.max(axis=1) - ratings.min(axis=1)
    pct_identical = float((ranges == 0).mean() * 100)
    max_range = int(ranges.max())
    mean_range = float(ranges.mean())

    return StabilityMetrics(
        dimension_id=dimension_id,
        n_adrs=n_adrs,
        n_passes=n_passes,
        icc_3k=icc,
        icc_3k_ci=icc_ci,
        mean_within_std=round(mean_within_std, 4),
        pct_identical=round(pct_identical, 2),
        max_range=max_range,
        mean_range=round(mean_range, 4),
    )


def prompt_sensitivity_analysis(
    variant_scores: dict[str, dict[str, list[int]]],
    dimension_id: str = "overall",
) -> dict:
    """Analyze sensitivity to prompt variations (Step 4.5).

    Tests whether different prompt variants produce significantly different scores.

    Args:
        variant_scores: Dict mapping variant_name to dict of adr_filename -> score.
        dimension_id: Dimension identifier.

    Returns:
        Dict with sensitivity analysis results.
    """
    variant_names = list(variant_scores.keys())
    if len(variant_names) < 2:
        return {"dimension_id": dimension_id, "error": "Need ≥2 variants"}

    # Get common ADR filenames across all variants
    common_adrs = set.intersection(
        *[set(variant_scores[v].keys()) for v in variant_names]
    )
    common_adrs = sorted(common_adrs)

    if len(common_adrs) < 5:
        return {"dimension_id": dimension_id, "error": "Too few common ADRs"}

    # Build score arrays
    arrays = {}
    for v in variant_names:
        arrays[v] = np.array([variant_scores[v][a] for a in common_adrs])

    # Friedman test across variants
    try:
        chi2, p_val = stats.friedmanchisquare(*arrays.values())
    except ValueError:
        chi2, p_val = 0.0, 1.0

    # Count ADRs where any variant diverges by >1 point
    all_scores = np.column_stack(list(arrays.values()))
    ranges = all_scores.max(axis=1) - all_scores.min(axis=1)
    pct_divergent = float((ranges > 1).mean() * 100)

    # Variance decomposition: prompt variance vs. ADR variance
    adr_means = all_scores.mean(axis=1)
    total_var = all_scores.var()
    adr_var = adr_means.var()
    prompt_var = total_var - adr_var if total_var > 0 else 0

    return {
        "dimension_id": dimension_id,
        "n_adrs": len(common_adrs),
        "n_variants": len(variant_names),
        "variant_names": variant_names,
        "friedman_chi2": round(float(chi2), 4),
        "friedman_p": round(float(p_val), 6),
        "pct_divergent_gt1": round(pct_divergent, 2),
        "total_variance": round(float(total_var), 4),
        "adr_variance": round(float(adr_var), 4),
        "prompt_variance": round(float(prompt_var), 4),
        "variance_explained_by_prompt": (
            round(float(prompt_var / total_var * 100), 2) if total_var > 0 else 0
        ),
        "is_sensitive": pct_divergent > 10,  # Flag if >10% of ADRs diverge by >1
    }


def cross_cohort_validation(
    cohort_scores: dict[str, dict[str, list[int]]],
    dimension_id: str = "overall",
) -> dict:
    """Leave-one-cohort-out cross-validation (Step 4.4).

    Tests whether prompts developed on one cohort generalize to others.

    Args:
        cohort_scores: Dict mapping cohort_name to dict of adr_filename -> scores.
        dimension_id: Dimension identifier.

    Returns:
        Dict with per-cohort generalization results.
    """
    cohort_names = list(cohort_scores.keys())
    results = {
        "dimension_id": dimension_id,
        "n_cohorts": len(cohort_names),
        "cohort_results": {},
    }

    for held_out in cohort_names:
        train_cohorts = [c for c in cohort_names if c != held_out]

        # Aggregate train scores for comparison
        train_scores = []
        for c in train_cohorts:
            for scores in cohort_scores[c].values():
                train_scores.extend(scores)

        test_scores = []
        for scores in cohort_scores[held_out].values():
            test_scores.extend(scores)

        if not train_scores or not test_scores:
            continue

        # Compare distributions
        try:
            ks_stat, ks_p = stats.ks_2samp(train_scores, test_scores)
        except ValueError:
            ks_stat, ks_p = 0.0, 1.0

        results["cohort_results"][held_out] = {
            "n_train": len(train_scores),
            "n_test": len(test_scores),
            "train_mean": round(float(np.mean(train_scores)), 4),
            "test_mean": round(float(np.mean(test_scores)), 4),
            "ks_statistic": round(float(ks_stat), 4),
            "ks_p_value": round(float(ks_p), 6),
            "generalizes": ks_p > 0.05,
        }

    return results
