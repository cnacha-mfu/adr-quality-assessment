"""Tests for score aggregation and feedback generation."""

from adr_analyser.aggregation.aggregator import (
    AggregatedScore,
    QualityTier,
    aggregate_scores,
    classify_tier,
)
from adr_analyser.feedback.generator import generate_template_feedback


def test_classify_tier():
    """Quality tier classification should match defined thresholds."""
    assert classify_tier(4.0) == QualityTier.EXCELLENT
    assert classify_tier(3.5) == QualityTier.EXCELLENT
    assert classify_tier(3.0) == QualityTier.GOOD
    assert classify_tier(2.5) == QualityTier.GOOD
    assert classify_tier(2.0) == QualityTier.NEEDS_IMPROVEMENT
    assert classify_tier(1.5) == QualityTier.NEEDS_IMPROVEMENT
    assert classify_tier(1.0) == QualityTier.POOR
    assert classify_tier(1.4) == QualityTier.POOR


def test_aggregate_scores_equal_weights():
    """Aggregation with equal weights should produce the mean."""
    scores = {
        "A1": 3, "A2": 3, "B1": 3, "B2": 3, "B3": 3,
        "B4": 3, "B5": 3, "C1": 3, "C2": 3, "C3": 3,
    }
    result = aggregate_scores("test.md", scores)

    assert result.weighted_composite == 3.0
    assert result.tier == QualityTier.GOOD
    assert result.min_score == 3
    assert result.max_score == 3
    assert result.std_dev == 0.0


def test_aggregate_scores_mixed():
    """Aggregation should correctly identify min/max dimensions."""
    scores = {
        "A1": 4, "A2": 3, "B1": 2, "B2": 1, "B3": 3,
        "B4": 2, "B5": 3, "C1": 4, "C2": 3, "C3": 1,
    }
    result = aggregate_scores("mixed.md", scores)

    assert result.min_score == 1
    assert result.max_score == 4
    assert result.std_dev > 0
    assert result.tier in (QualityTier.GOOD, QualityTier.NEEDS_IMPROVEMENT)


def test_aggregate_category_scores():
    """Category scores should be computed correctly."""
    scores = {
        "A1": 4, "A2": 4,  # Structural avg = 4.0
        "B1": 2, "B2": 2, "B3": 2, "B4": 2, "B5": 2,  # Content avg = 2.0
        "C1": 3, "C2": 3, "C3": 3,  # Documentation avg = 3.0
    }
    result = aggregate_scores("test.md", scores)

    assert result.category_scores["structural"] == 4.0
    assert result.category_scores["content"] == 2.0
    assert result.category_scores["documentation"] == 3.0


def test_generate_template_feedback():
    """Template feedback should produce strengths and improvements."""
    scores = {
        "A1": 4, "A2": 3, "B1": 2, "B2": 1, "B3": 3,
        "B4": 2, "B5": 3, "C1": 3, "C2": 3, "C3": 1,
    }
    aggregated = aggregate_scores("test.md", scores)
    feedback = generate_template_feedback(aggregated)

    assert feedback.adr_filename == "test.md"
    assert len(feedback.strengths) >= 1
    assert len(feedback.improvements) >= 1
    assert feedback.tier in ("Excellent", "Good", "Needs Improvement", "Poor")
    assert "overall" in feedback.overall_assessment.lower() or \
           "quality" in feedback.overall_assessment.lower() or \
           "adr" in feedback.overall_assessment.lower()
