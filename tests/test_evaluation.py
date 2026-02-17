"""Tests for evaluation metrics (agreement, comparison, stability, IRR)."""

import numpy as np

from adr_analyser.evaluation.agreement import (
    bland_altman_data,
    compute_agreement,
    compute_qwk,
)
from adr_analyser.evaluation.comparison import (
    compare_models,
    compute_cliffs_delta,
    holm_bonferroni,
)
from adr_analyser.evaluation.stability import compute_stability
from adr_analyser.evaluation.irr import compute_irr, krippendorff_alpha_ordinal


# -- Agreement tests --

def test_qwk_perfect_agreement():
    """QWK should be 1.0 for perfect agreement."""
    y = np.array([1, 2, 3, 4, 1, 2, 3, 4])
    assert compute_qwk(y, y) == 1.0


def test_qwk_reasonable_agreement():
    """QWK should be positive for reasonable agreement."""
    y_true = np.array([1, 2, 3, 4, 2, 3, 4, 1])
    y_pred = np.array([1, 2, 3, 4, 3, 3, 3, 1])
    qwk = compute_qwk(y_true, y_pred)
    assert 0.5 < qwk < 1.0


def test_compute_agreement():
    """compute_agreement should return all metrics."""
    y_true = [1, 2, 3, 4, 2, 3, 4, 1, 2, 3]
    y_pred = [1, 2, 3, 4, 3, 3, 3, 1, 2, 3]
    metrics = compute_agreement(y_true, y_pred, "B3")

    assert metrics.dimension_id == "B3"
    assert metrics.n == 10
    assert 0.5 <= metrics.spearman_rho <= 1.0
    assert 0 < metrics.qwk <= 1.0
    assert metrics.mae >= 0
    assert metrics.rmse >= 0
    assert 0 <= metrics.exact_agreement <= 100
    assert metrics.adjacent_agreement >= metrics.exact_agreement


def test_bland_altman():
    """Bland-Altman analysis should compute bias and limits of agreement."""
    y_true = [1, 2, 3, 4, 2, 3]
    y_pred = [2, 2, 3, 4, 3, 3]
    ba = bland_altman_data(y_true, y_pred)

    assert ba["n"] == 6
    assert ba["bias"] <= 0  # Slight negative bias (LLM scores higher)
    assert ba["lower_loa"] < ba["bias"] < ba["upper_loa"]


# -- Comparison tests --

def test_cliffs_delta_identical():
    """Cliff's delta should be 0 for identical distributions."""
    x = np.array([1, 2, 3, 4])
    y = np.array([1, 2, 3, 4])
    cd = compute_cliffs_delta(x, y)
    assert cd.delta == 0.0
    assert cd.interpretation == "negligible"


def test_cliffs_delta_large():
    """Cliff's delta should be large for very different distributions."""
    x = np.array([1, 1, 1, 1, 1])
    y = np.array([4, 4, 4, 4, 4])
    cd = compute_cliffs_delta(x, y)
    assert abs(cd.delta) >= 0.9
    assert cd.interpretation == "large"


def test_holm_bonferroni():
    """Holm-Bonferroni should correctly adjust p-values."""
    p_values = [0.01, 0.04, 0.03, 0.005]
    adjusted = holm_bonferroni(p_values)

    # All adjusted values should be >= original values
    for orig, adj in zip(p_values, adjusted):
        assert adj >= orig

    # Most significant should still be significant
    assert adjusted[p_values.index(0.005)] < 0.05


def test_compare_models():
    """compare_models should produce Friedman + pairwise results."""
    scores = {
        "gemini": [3, 3, 4, 2, 3, 4, 2, 3, 3, 4],
        "prometheus": [2, 3, 3, 2, 2, 3, 2, 3, 3, 3],
        "llama": [3, 2, 4, 1, 3, 4, 1, 2, 3, 3],
    }
    result = compare_models(scores, "B3")

    assert result.dimension_id == "B3"
    assert result.n == 10
    assert len(result.pairwise) == 3  # C(3,2) = 3 pairs


# -- Stability tests --

def test_stability_identical_passes():
    """Stability should be perfect for identical passes."""
    multi_pass = {
        "adr1.md": [3, 3, 3, 3, 3],
        "adr2.md": [2, 2, 2, 2, 2],
        "adr3.md": [4, 4, 4, 4, 4],
    }
    result = compute_stability(multi_pass, "A1")

    assert result.pct_identical == 100.0
    assert result.max_range == 0
    assert result.mean_within_std == 0.0


def test_stability_variable_passes():
    """Stability metrics should reflect variability in passes."""
    multi_pass = {
        "adr1.md": [3, 3, 4, 3, 2],
        "adr2.md": [2, 3, 2, 2, 2],
        "adr3.md": [4, 4, 4, 3, 4],
    }
    result = compute_stability(multi_pass, "A1")

    assert result.pct_identical < 100
    assert result.max_range >= 1
    assert result.mean_within_std > 0


# -- IRR tests --

def test_krippendorff_perfect_agreement():
    """Krippendorff's alpha should be ~1.0 for perfect agreement."""
    data = [
        [1, 2, 3, 4, 1, 2, 3, 4],
        [1, 2, 3, 4, 1, 2, 3, 4],
    ]
    alpha = krippendorff_alpha_ordinal(data)
    assert alpha > 0.99


def test_krippendorff_some_agreement():
    """Krippendorff's alpha should be moderate for partial agreement."""
    data = [
        [1, 2, 3, 4, 2, 3, 4, 1, 2, 3],
        [1, 2, 3, 4, 3, 3, 3, 1, 2, 3],
    ]
    alpha = krippendorff_alpha_ordinal(data)
    assert 0.5 < alpha < 1.0


def test_compute_irr():
    """compute_irr should produce all IRR metrics."""
    annotations = {
        "annotator_1": {
            "adr1.md": [3], "adr2.md": [2], "adr3.md": [4],
            "adr4.md": [1], "adr5.md": [3], "adr6.md": [2],
        },
        "annotator_2": {
            "adr1.md": [3], "adr2.md": [2], "adr3.md": [4],
            "adr4.md": [2], "adr5.md": [3], "adr6.md": [2],
        },
    }
    result = compute_irr(annotations, "B3")

    assert result.dimension_id == "B3"
    assert result.n_items == 6
    assert result.n_raters == 2
    assert result.krippendorff_alpha > 0.5
    assert 0 <= result.exact_agreement_pct <= 100
