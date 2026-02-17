"""
Agreement Analysis for RQ1 (Step 4.2).

Computes the full metric suite for evaluating LLM-human agreement:
- Spearman's ρ (primary rank correlation)
- Quadratic weighted Cohen's kappa (QWK) — standard in automated essay scoring
- ICC(2,1) for absolute agreement with 95% CI
- Mean absolute error (MAE) and RMSE
- Exact agreement % and adjacent agreement % (within ±1)
- Bland-Altman analysis (bias and limits of agreement)

All metrics are computed per dimension and overall.

Critical benchmark: compare LLM-human agreement against human-human
inter-annotator agreement.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class AgreementMetrics:
    """Complete agreement metrics between two raters (or rater vs. LLM)."""

    dimension_id: str
    n: int  # Number of items
    spearman_rho: float
    spearman_p: float
    qwk: float  # Quadratic weighted kappa
    icc_21: float  # ICC(2,1) absolute agreement
    icc_95_ci: tuple[float, float]  # 95% CI for ICC
    mae: float  # Mean absolute error
    rmse: float  # Root mean squared error
    exact_agreement: float  # Percentage of identical scores
    adjacent_agreement: float  # Percentage within ±1


def compute_qwk(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int = 4) -> float:
    """Compute Quadratic Weighted Cohen's Kappa.

    This is the standard metric in automated essay scoring (ASAP competition).
    QWK penalizes larger disagreements more heavily than simple kappa.

    Args:
        y_true: Ground truth scores.
        y_pred: Predicted scores.
        num_classes: Number of score classes (default: 4 for 1-4 scale).

    Returns:
        Quadratic weighted kappa value.
    """
    # Build confusion matrix
    min_rating = 1
    max_rating = num_classes

    conf_mat = np.zeros((num_classes, num_classes), dtype=float)
    for t, p in zip(y_true, y_pred):
        conf_mat[int(t) - min_rating][int(p) - min_rating] += 1

    n = conf_mat.sum()
    if n == 0:
        return 0.0

    # Weight matrix (quadratic weights)
    weight_mat = np.zeros((num_classes, num_classes), dtype=float)
    for i in range(num_classes):
        for j in range(num_classes):
            weight_mat[i][j] = (i - j) ** 2 / (num_classes - 1) ** 2

    # Expected matrix under independence
    row_sums = conf_mat.sum(axis=1)
    col_sums = conf_mat.sum(axis=0)
    expected = np.outer(row_sums, col_sums) / n

    # QWK formula
    numerator = (weight_mat * conf_mat).sum()
    denominator = (weight_mat * expected).sum()

    if denominator == 0:
        return 1.0 if numerator == 0 else 0.0

    return 1.0 - numerator / denominator


def compute_icc_21(
    ratings: np.ndarray,
    n_bootstrap: int = 10000,
    ci_level: float = 0.95,
    seed: int = 42,
) -> tuple[float, tuple[float, float]]:
    """Compute ICC(2,1) for absolute agreement with bootstrap CI.

    ICC(2,1) treats raters as a random sample from a population of raters
    and assesses absolute agreement (not just consistency).

    Args:
        ratings: Array of shape (n_subjects, n_raters).
        n_bootstrap: Number of bootstrap resamples for CI.
        ci_level: Confidence level for CI.
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (ICC value, (lower_CI, upper_CI)).
    """
    n, k = ratings.shape
    if n < 2 or k < 2:
        return 0.0, (0.0, 0.0)

    def _compute_icc(data):
        n, k = data.shape
        grand_mean = data.mean()
        row_means = data.mean(axis=1)
        col_means = data.mean(axis=0)

        # Sum of squares
        ss_total = ((data - grand_mean) ** 2).sum()
        ss_rows = k * ((row_means - grand_mean) ** 2).sum()
        ss_cols = n * ((col_means - grand_mean) ** 2).sum()
        ss_error = ss_total - ss_rows - ss_cols

        # Mean squares
        ms_rows = ss_rows / (n - 1) if n > 1 else 0
        ms_cols = ss_cols / (k - 1) if k > 1 else 0
        ms_error = ss_error / ((n - 1) * (k - 1)) if (n > 1 and k > 1) else 0

        # ICC(2,1) formula
        denom = ms_rows + (k - 1) * ms_error + k * (ms_cols - ms_error) / n
        if denom == 0:
            return 0.0
        return (ms_rows - ms_error) / denom

    icc = _compute_icc(ratings)

    # Bootstrap CI (BCa)
    rng = np.random.RandomState(seed)
    boot_iccs = []
    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, size=n)
        boot_data = ratings[idx, :]
        boot_iccs.append(_compute_icc(boot_data))

    boot_iccs = np.array(boot_iccs)
    alpha = 1 - ci_level
    lower = np.percentile(boot_iccs, 100 * alpha / 2)
    upper = np.percentile(boot_iccs, 100 * (1 - alpha / 2))

    return icc, (round(lower, 4), round(upper, 4))


def compute_agreement(
    y_true: list[int],
    y_pred: list[int],
    dimension_id: str = "overall",
) -> AgreementMetrics:
    """Compute the full agreement metric suite.

    Args:
        y_true: Ground truth scores (human annotations).
        y_pred: Predicted scores (LLM or baseline).
        dimension_id: Identifier for the dimension being evaluated.

    Returns:
        AgreementMetrics with all computed statistics.
    """
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    n = len(y_true)

    if n < 2:
        return AgreementMetrics(
            dimension_id=dimension_id, n=n,
            spearman_rho=0, spearman_p=1, qwk=0, icc_21=0,
            icc_95_ci=(0, 0), mae=0, rmse=0,
            exact_agreement=0, adjacent_agreement=0,
        )

    # Spearman's rho
    rho, p_val = stats.spearmanr(y_true, y_pred)

    # QWK
    qwk = compute_qwk(y_true, y_pred)

    # ICC(2,1)
    ratings = np.column_stack([y_true, y_pred])
    icc, icc_ci = compute_icc_21(ratings)

    # MAE and RMSE
    errors = np.abs(y_true - y_pred)
    mae = errors.mean()
    rmse = np.sqrt(((y_true - y_pred) ** 2).mean())

    # Exact and adjacent agreement
    exact = (y_true == y_pred).mean() * 100
    adjacent = (errors <= 1).mean() * 100

    return AgreementMetrics(
        dimension_id=dimension_id,
        n=n,
        spearman_rho=round(float(rho), 4),
        spearman_p=round(float(p_val), 6),
        qwk=round(float(qwk), 4),
        icc_21=round(float(icc), 4),
        icc_95_ci=icc_ci,
        mae=round(float(mae), 4),
        rmse=round(float(rmse), 4),
        exact_agreement=round(float(exact), 2),
        adjacent_agreement=round(float(adjacent), 2),
    )


def bland_altman_data(
    y_true: list[int],
    y_pred: list[int],
) -> dict:
    """Compute Bland-Altman analysis data for plotting.

    The Bland-Altman plot shows the difference between two measurements
    against their mean, revealing systematic bias and limits of agreement.

    Args:
        y_true: Ground truth scores.
        y_pred: Predicted scores.

    Returns:
        Dict with means, differences, bias, and limits of agreement.
    """
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)

    means = (y_true + y_pred) / 2
    diffs = y_true - y_pred

    bias = diffs.mean()
    std_diff = diffs.std(ddof=1)

    return {
        "means": means.tolist(),
        "differences": diffs.tolist(),
        "bias": round(float(bias), 4),
        "upper_loa": round(float(bias + 1.96 * std_diff), 4),
        "lower_loa": round(float(bias - 1.96 * std_diff), 4),
        "std_diff": round(float(std_diff), 4),
        "n": len(y_true),
    }
