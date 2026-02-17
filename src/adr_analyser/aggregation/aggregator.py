"""
Score Aggregation: Stage 4 of the assessment pipeline.

Computes weighted composite scores, classification tiers,
and summary statistics from per-dimension scores.

Classification tiers (on the 4-point scale):
- Excellent: ≥ 3.5
- Good: 2.5–3.49
- Needs Improvement: 1.5–2.49
- Poor: < 1.5
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from adr_analyser.quality_model.dimensions import DIMENSION_ORDER, QUALITY_MODEL, QualityCategory


class QualityTier(str, Enum):
    """Classification tier for overall ADR quality."""

    EXCELLENT = "Excellent"
    GOOD = "Good"
    NEEDS_IMPROVEMENT = "Needs Improvement"
    POOR = "Poor"


@dataclass
class AggregatedScore:
    """Aggregated quality assessment for a single ADR."""

    adr_filename: str
    dimension_scores: dict[str, int]  # dim_id -> median score
    weighted_composite: float
    tier: QualityTier
    min_score: int  # Weakest dimension score
    max_score: int  # Strongest dimension score
    min_dimension: str  # ID of weakest dimension
    max_dimension: str  # ID of strongest dimension
    std_dev: float  # Standard deviation across dimensions
    category_scores: dict[str, float]  # Category -> average score
    weights_used: dict[str, float]  # Dimension -> weight used


# Default equal weights (to be updated after Delphi validation, Step 1.2)
DEFAULT_WEIGHTS: dict[str, float] = {dim_id: 1.0 for dim_id in DIMENSION_ORDER}


def classify_tier(score: float) -> QualityTier:
    """Classify a composite score into a quality tier."""
    if score >= 3.5:
        return QualityTier.EXCELLENT
    elif score >= 2.5:
        return QualityTier.GOOD
    elif score >= 1.5:
        return QualityTier.NEEDS_IMPROVEMENT
    else:
        return QualityTier.POOR


def aggregate_scores(
    adr_filename: str,
    dimension_scores: dict[str, int],
    weights: Optional[dict[str, float]] = None,
) -> AggregatedScore:
    """Aggregate per-dimension scores into a composite assessment.

    Args:
        adr_filename: ADR identifier.
        dimension_scores: Dict mapping dimension_id to integer score (1-4).
        weights: Optional dimension weights. Defaults to equal weights.

    Returns:
        AggregatedScore with composite score and classification.
    """
    weights = weights or DEFAULT_WEIGHTS

    # Compute weighted composite
    total_weight = 0.0
    weighted_sum = 0.0
    for dim_id, score in dimension_scores.items():
        w = weights.get(dim_id, 1.0)
        weighted_sum += score * w
        total_weight += w

    weighted_composite = weighted_sum / total_weight if total_weight > 0 else 0.0

    # Find min/max dimensions
    scores_list = list(dimension_scores.values())
    min_score = min(scores_list) if scores_list else 0
    max_score = max(scores_list) if scores_list else 0

    min_dim = min(dimension_scores, key=dimension_scores.get) if dimension_scores else ""
    max_dim = max(dimension_scores, key=dimension_scores.get) if dimension_scores else ""

    # Standard deviation across dimensions
    std_dev = statistics.stdev(scores_list) if len(scores_list) > 1 else 0.0

    # Category averages
    category_scores = {}
    for cat in QualityCategory:
        cat_dims = [
            dim_id
            for dim_id, dim in QUALITY_MODEL.items()
            if dim.category == cat and dim_id in dimension_scores
        ]
        if cat_dims:
            cat_avg = statistics.mean([dimension_scores[d] for d in cat_dims])
            category_scores[cat.value] = round(cat_avg, 2)

    return AggregatedScore(
        adr_filename=adr_filename,
        dimension_scores=dimension_scores,
        weighted_composite=round(weighted_composite, 2),
        tier=classify_tier(weighted_composite),
        min_score=min_score,
        max_score=max_score,
        min_dimension=min_dim,
        max_dimension=max_dim,
        std_dev=round(std_dev, 2),
        category_scores=category_scores,
        weights_used=weights,
    )
