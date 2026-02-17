"""Tests for the quality model dimensions and rubric."""

from adr_analyser.quality_model.dimensions import (
    DIMENSION_ORDER,
    QUALITY_MODEL,
    QualityCategory,
    get_dimension,
    get_dimensions_by_category,
)
from adr_analyser.quality_model.rubric import SCORING_RUBRIC


def test_all_10_dimensions_defined():
    """The quality model should have exactly 10 dimensions."""
    assert len(QUALITY_MODEL) == 10
    assert len(DIMENSION_ORDER) == 10


def test_dimension_ids():
    """Dimension IDs should follow the A1, A2, B1-B5, C1-C3 pattern."""
    expected = {"A1", "A2", "B1", "B2", "B3", "B4", "B5", "C1", "C2", "C3"}
    assert set(QUALITY_MODEL.keys()) == expected


def test_each_dimension_has_4_anchors():
    """Each dimension should have exactly 4 scale anchors (1-4)."""
    for dim_id, dim in QUALITY_MODEL.items():
        assert len(dim.anchors) == 4, f"{dim_id} has {len(dim.anchors)} anchors"
        scores = [a.score for a in dim.anchors]
        assert scores == [1, 2, 3, 4], f"{dim_id} anchors are {scores}"


def test_categories():
    """Dimensions should be organized into 3 categories."""
    structural = get_dimensions_by_category(QualityCategory.STRUCTURAL)
    content = get_dimensions_by_category(QualityCategory.CONTENT)
    documentation = get_dimensions_by_category(QualityCategory.DOCUMENTATION)

    assert len(structural) == 2  # A1, A2
    assert len(content) == 5  # B1-B5
    assert len(documentation) == 3  # C1-C3


def test_get_dimension():
    """get_dimension should return correct dimension."""
    dim = get_dimension("B3")
    assert dim.id == "B3"
    assert dim.name == "Rationale Depth"
    assert dim.category == QualityCategory.CONTENT


def test_get_dimension_invalid():
    """get_dimension should raise KeyError for invalid ID."""
    try:
        get_dimension("X1")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_gqm_entries():
    """Every dimension should have a GQM entry with goal, questions, and metrics."""
    for dim_id, dim in QUALITY_MODEL.items():
        assert dim.gqm.goal, f"{dim_id} missing GQM goal"
        assert len(dim.gqm.questions) >= 3, f"{dim_id} has too few GQM questions"
        assert len(dim.gqm.metrics) >= 2, f"{dim_id} has too few GQM metrics"


def test_rubric_exists_for_all_dimensions():
    """Every dimension should have a corresponding rubric entry."""
    for dim_id in DIMENSION_ORDER:
        assert dim_id in SCORING_RUBRIC, f"Missing rubric for {dim_id}"


def test_rubric_has_anchor_examples():
    """Each rubric should have at least 3 anchor examples."""
    for dim_id, rubric in SCORING_RUBRIC.items():
        assert len(rubric.anchor_examples) >= 3, (
            f"{dim_id} has only {len(rubric.anchor_examples)} examples"
        )


def test_rubric_covers_score_range():
    """Each rubric should have examples at score 1 and score 4."""
    for dim_id, rubric in SCORING_RUBRIC.items():
        scores = [ex.score for ex in rubric.anchor_examples]
        assert 1 in scores, f"{dim_id} rubric missing score-1 example"
        assert 4 in scores, f"{dim_id} rubric missing score-4 example"
