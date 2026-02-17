"""
Non-LLM baselines for comparison (Step 3.4).

Implements four baselines that reviewers will expect to see:
1. Random scoring: scores drawn from the same distribution as human labels
2. Section-count heuristic: completeness proxy based on MADR section presence
3. Word-count regression: linear model predicting quality from word count
4. TF-IDF + Ridge Regression: trained on expert-annotated data with cross-validation

These establish that the LLM adds genuine value beyond surface features.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Optional

import numpy as np

from adr_analyser.parsing.parser import ParsedADR
from adr_analyser.parsing.section_extractor import ExtractedSections, extract_sections
from adr_analyser.quality_model.dimensions import DIMENSION_ORDER


class RandomBaseline:
    """Baseline 1: Random scoring from the same distribution as human labels.

    After human annotation is complete, fit the distribution of human scores
    per dimension and sample from it.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self._distributions: dict[str, list[float]] = {}

    def fit(self, human_scores: dict[str, list[int]]) -> None:
        """Fit the distribution from human annotations.

        Args:
            human_scores: Dict mapping dimension_id to list of all human scores.
        """
        for dim_id, scores in human_scores.items():
            # Compute probability distribution
            counter = Counter(scores)
            total = len(scores)
            self._distributions[dim_id] = [
                counter.get(s, 0) / total for s in range(1, 5)
            ]

    def predict(self, adr: ParsedADR) -> dict[str, int]:
        """Generate random scores for an ADR (content-independent).

        Args:
            adr: Parsed ADR (unused; scores are random).

        Returns:
            Dict mapping dimension_id to random score (1-4).
        """
        scores = {}
        for dim_id in DIMENSION_ORDER:
            if dim_id in self._distributions:
                weights = self._distributions[dim_id]
                scores[dim_id] = self.rng.choices([1, 2, 3, 4], weights=weights, k=1)[0]
            else:
                # Uniform distribution if no human data available
                scores[dim_id] = self.rng.randint(1, 4)
        return scores


class SectionCountBaseline:
    """Baseline 2: Section-count heuristic.

    Maps the number of detected MADR sections to a quality score.
    Primarily predicts completeness (A1) but applies a heuristic
    mapping to other dimensions as well.
    """

    # Section count thresholds for quality tiers
    _THRESHOLDS = {
        # (min_mandatory, min_optional) -> base score
        (3, 3): 4,  # All mandatory + 3+ optional = Excellent
        (3, 1): 3,  # All mandatory + 1-2 optional = Good
        (2, 0): 2,  # Most mandatory, few optional = Needs Improvement
        (0, 0): 1,  # Minimal sections = Poor
    }

    def predict(self, adr: ParsedADR) -> dict[str, int]:
        """Predict quality scores based on section count heuristic.

        Args:
            adr: Parsed ADR.

        Returns:
            Dict mapping dimension_id to heuristic score (1-4).
        """
        sections = extract_sections(adr)
        mandatory = sections.mandatory_sections_present
        optional = sections.optional_sections_present

        # Determine base score from thresholds
        base_score = 1
        for (min_mand, min_opt), score in sorted(
            self._THRESHOLDS.items(), reverse=True
        ):
            if mandatory >= min_mand and optional >= min_opt:
                base_score = score
                break

        # Apply dimension-specific adjustments
        scores = {}
        for dim_id in DIMENSION_ORDER:
            if dim_id == "A1":
                # Completeness directly maps to section count
                scores[dim_id] = base_score
            elif dim_id == "A2":
                # Structural conformance: check heading count and consistency
                heading_score = min(4, max(1, len(adr.headings) // 2))
                scores[dim_id] = min(base_score, heading_score)
            elif dim_id in ("B1", "B2", "B3", "B4", "B5"):
                # Content dimensions: slightly lower than base if sections sparse
                scores[dim_id] = max(1, base_score - (1 if optional < 2 else 0))
            else:
                # Documentation dimensions: harder to assess from sections alone
                scores[dim_id] = max(1, base_score - 1)

        return scores


class WordCountBaseline:
    """Baseline 3: Word-count regression.

    Linear model predicting quality from word count.
    Trained on expert-annotated data with cross-validation.
    """

    def __init__(self):
        self._coefficients: dict[str, tuple[float, float]] = {}  # dim_id -> (slope, intercept)
        self._fitted = False

    def fit(
        self,
        word_counts: list[int],
        scores: dict[str, list[int]],
    ) -> None:
        """Fit linear regression per dimension from word count.

        Args:
            word_counts: List of word counts for each ADR.
            scores: Dict mapping dimension_id to list of scores (aligned with word_counts).
        """
        x = np.array(word_counts, dtype=float)

        for dim_id, y_list in scores.items():
            y = np.array(y_list, dtype=float)
            if len(x) != len(y) or len(x) < 2:
                continue

            # Simple linear regression
            x_mean = x.mean()
            y_mean = y.mean()
            ss_xy = ((x - x_mean) * (y - y_mean)).sum()
            ss_xx = ((x - x_mean) ** 2).sum()

            if ss_xx > 0:
                slope = ss_xy / ss_xx
                intercept = y_mean - slope * x_mean
            else:
                slope = 0.0
                intercept = y_mean

            self._coefficients[dim_id] = (slope, intercept)

        self._fitted = True

    def predict(self, adr: ParsedADR) -> dict[str, int]:
        """Predict quality scores from word count.

        Args:
            adr: Parsed ADR.

        Returns:
            Dict mapping dimension_id to predicted score (1-4).
        """
        scores = {}
        wc = adr.word_count

        for dim_id in DIMENSION_ORDER:
            if dim_id in self._coefficients:
                slope, intercept = self._coefficients[dim_id]
                raw = slope * wc + intercept
                scores[dim_id] = max(1, min(4, round(raw)))
            else:
                # Fallback: simple heuristic based on word count
                if wc < 50:
                    scores[dim_id] = 1
                elif wc < 150:
                    scores[dim_id] = 2
                elif wc < 400:
                    scores[dim_id] = 3
                else:
                    scores[dim_id] = 4

        return scores


class TFIDFBaseline:
    """Baseline 4: TF-IDF + Ridge Regression.

    Trained on expert-annotated data with cross-validation.
    Uses scikit-learn for TF-IDF vectorization and Ridge regression.
    """

    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self._vectorizers: dict[str, object] = {}
        self._models: dict[str, object] = {}
        self._fitted = False

    def fit(
        self,
        texts: list[str],
        scores: dict[str, list[int]],
        cv_folds: int = 5,
    ) -> dict[str, dict]:
        """Fit TF-IDF + Ridge per dimension with cross-validation.

        Args:
            texts: List of ADR content strings.
            scores: Dict mapping dimension_id to list of scores.
            cv_folds: Number of cross-validation folds.

        Returns:
            Dict with cross-validation results per dimension.
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import RidgeCV
        from sklearn.model_selection import cross_val_score

        cv_results = {}

        for dim_id, y_list in scores.items():
            y = np.array(y_list, dtype=float)
            if len(texts) != len(y) or len(texts) < cv_folds:
                continue

            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words="english",
            )
            X = vectorizer.fit_transform(texts)

            # Ridge regression with cross-validation for alpha selection
            model = RidgeCV(alphas=[0.1, 1.0, 10.0])
            model.fit(X, y)

            # Cross-validation scores
            cv_scores = cross_val_score(
                model, X, y, cv=min(cv_folds, len(texts)), scoring="neg_mean_squared_error"
            )

            self._vectorizers[dim_id] = vectorizer
            self._models[dim_id] = model
            cv_results[dim_id] = {
                "mean_mse": -cv_scores.mean(),
                "std_mse": cv_scores.std(),
                "best_alpha": model.alpha_,
            }

        self._fitted = True
        return cv_results

    def predict(self, adr: ParsedADR) -> dict[str, int]:
        """Predict quality scores using TF-IDF features.

        Args:
            adr: Parsed ADR.

        Returns:
            Dict mapping dimension_id to predicted score (1-4).
        """
        if not self._fitted:
            raise RuntimeError("Model not fitted. Call fit() first with annotated data.")

        scores = {}
        for dim_id in DIMENSION_ORDER:
            if dim_id in self._models:
                vectorizer = self._vectorizers[dim_id]
                model = self._models[dim_id]
                X = vectorizer.transform([adr.body])
                raw = model.predict(X)[0]
                scores[dim_id] = max(1, min(4, round(raw)))
            else:
                scores[dim_id] = 2  # Default fallback

        return scores
