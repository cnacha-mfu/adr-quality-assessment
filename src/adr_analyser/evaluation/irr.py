"""
Inter-Rater Reliability (IRR) computation for Phase 2 (Step 2.5).

Computes and reports:
- Krippendorff's alpha (ordinal) — primary IRR metric
- Quadratic weighted Cohen's kappa — pairwise
- ICC(2,1) for absolute agreement with 95% bootstrap CI
- Per-dimension IRR to identify hard-to-rate quality aspects
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class IRRResult:
    """Inter-rater reliability results for a dimension."""

    dimension_id: str
    n_items: int
    n_raters: int
    krippendorff_alpha: float
    cohens_kappa_pairwise: dict[tuple[str, str], float]  # (rater_a, rater_b) -> kappa
    icc_21: float
    icc_95_ci: tuple[float, float]
    exact_agreement_pct: float
    adjacent_agreement_pct: float
    interpretation: str  # poor, fair, moderate, good, excellent


def krippendorff_alpha_ordinal(
    reliability_data: list[list[int | None]],
) -> float:
    """Compute Krippendorff's alpha for ordinal data.

    Args:
        reliability_data: List of rater lists. Each inner list contains scores
            for all items (or None for missing). Shape: [n_raters][n_items].

    Returns:
        Krippendorff's alpha value.
    """
    n_raters = len(reliability_data)
    n_items = len(reliability_data[0]) if reliability_data else 0

    if n_raters < 2 or n_items < 2:
        return 0.0

    # Collect all non-None values and their positions
    values_per_item = []
    all_values = []
    for i in range(n_items):
        item_values = []
        for r in range(n_raters):
            v = reliability_data[r][i]
            if v is not None:
                item_values.append(v)
                all_values.append(v)
        values_per_item.append(item_values)

    if len(all_values) < 4:
        return 0.0

    # Get unique values sorted
    unique_values = sorted(set(all_values))
    n_values = len(unique_values)
    value_to_idx = {v: i for i, v in enumerate(unique_values)}

    # Ordinal distance metric
    def ordinal_distance(v1, v2):
        i1 = value_to_idx[v1]
        i2 = value_to_idx[v2]
        return (i1 - i2) ** 2

    # Observed disagreement
    n_total = 0
    d_observed = 0.0
    for item_values in values_per_item:
        m = len(item_values)
        if m < 2:
            continue
        for j in range(m):
            for k in range(j + 1, m):
                d_observed += ordinal_distance(item_values[j], item_values[k])
                n_total += 1

    if n_total == 0:
        return 1.0

    d_observed /= n_total

    # Expected disagreement
    n_all = len(all_values)
    d_expected = 0.0
    n_pairs = 0
    for j in range(n_all):
        for k in range(j + 1, n_all):
            d_expected += ordinal_distance(all_values[j], all_values[k])
            n_pairs += 1

    if n_pairs == 0:
        return 1.0

    d_expected /= n_pairs

    if d_expected == 0:
        return 1.0

    return 1.0 - d_observed / d_expected


def compute_irr(
    annotations: dict[str, dict[str, list[int]]],
    dimension_id: str,
) -> IRRResult:
    """Compute IRR for a single dimension across all annotators.

    Args:
        annotations: Dict mapping annotator_id to dict of adr_filename -> [score].
            Each score list has one element (the score for this dimension).
        dimension_id: Dimension identifier.

    Returns:
        IRRResult with all IRR metrics.
    """
    from adr_analyser.evaluation.agreement import compute_icc_21, compute_qwk

    annotator_ids = list(annotations.keys())
    n_raters = len(annotator_ids)

    # Get common ADR filenames
    common_adrs = sorted(
        set.intersection(*[set(annotations[a].keys()) for a in annotator_ids])
    )
    n_items = len(common_adrs)

    if n_items < 2 or n_raters < 2:
        return IRRResult(
            dimension_id=dimension_id, n_items=n_items, n_raters=n_raters,
            krippendorff_alpha=0, cohens_kappa_pairwise={}, icc_21=0,
            icc_95_ci=(0, 0), exact_agreement_pct=0, adjacent_agreement_pct=0,
            interpretation="insufficient data",
        )

    # Build reliability data matrix
    reliability_data = []
    for a_id in annotator_ids:
        rater_scores = []
        for adr in common_adrs:
            scores = annotations[a_id].get(adr, [None])
            rater_scores.append(scores[0] if scores else None)
        reliability_data.append(rater_scores)

    # Krippendorff's alpha (ordinal)
    k_alpha = krippendorff_alpha_ordinal(reliability_data)

    # Pairwise QWK
    kappa_pairs = {}
    for i in range(n_raters):
        for j in range(i + 1, n_raters):
            scores_i = np.array([
                reliability_data[i][k] for k in range(n_items)
                if reliability_data[i][k] is not None and reliability_data[j][k] is not None
            ])
            scores_j = np.array([
                reliability_data[j][k] for k in range(n_items)
                if reliability_data[i][k] is not None and reliability_data[j][k] is not None
            ])
            if len(scores_i) > 1:
                kappa = compute_qwk(scores_i, scores_j)
                kappa_pairs[(annotator_ids[i], annotator_ids[j])] = round(kappa, 4)

    # ICC(2,1)
    ratings_matrix = np.array(reliability_data, dtype=float).T  # (n_items, n_raters)
    icc, icc_ci = compute_icc_21(ratings_matrix)

    # Exact and adjacent agreement (across all rater pairs)
    exact_matches = 0
    adjacent_matches = 0
    total_pairs = 0
    for k in range(n_items):
        for i in range(n_raters):
            for j in range(i + 1, n_raters):
                v_i = reliability_data[i][k]
                v_j = reliability_data[j][k]
                if v_i is not None and v_j is not None:
                    total_pairs += 1
                    if v_i == v_j:
                        exact_matches += 1
                    if abs(v_i - v_j) <= 1:
                        adjacent_matches += 1

    exact_pct = (exact_matches / total_pairs * 100) if total_pairs > 0 else 0
    adjacent_pct = (adjacent_matches / total_pairs * 100) if total_pairs > 0 else 0

    # Interpretation (Krippendorff's guidelines)
    if k_alpha >= 0.80:
        interp = "excellent"
    elif k_alpha >= 0.67:
        interp = "good (acceptable for some purposes)"
    elif k_alpha >= 0.50:
        interp = "moderate (only tentative conclusions)"
    else:
        interp = "poor (unreliable)"

    return IRRResult(
        dimension_id=dimension_id,
        n_items=n_items,
        n_raters=n_raters,
        krippendorff_alpha=round(k_alpha, 4),
        cohens_kappa_pairwise=kappa_pairs,
        icc_21=icc,
        icc_95_ci=icc_ci,
        exact_agreement_pct=round(exact_pct, 2),
        adjacent_agreement_pct=round(adjacent_pct, 2),
        interpretation=interp,
    )
