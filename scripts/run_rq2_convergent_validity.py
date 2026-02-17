#!/usr/bin/env python3
"""
RQ2: Convergent Validity Experiment

Research Question: Do LLM quality scores correlate meaningfully with
objective structural and textual features of ADRs?

Approach (Convergent/Discriminant Validity via MTMM-like matrix):
- Extract objective features from each ADR:
  * Structural: section count, heading count, has_metadata, heading consistency
  * Textual: word count, sentence count, Flesch-Kincaid readability, type-token ratio
  * Content: rationale word count, consequence count, reference count
- Correlate each feature with each LLM dimension score
- Convergent validity: features expected to correlate with specific dimensions SHOULD
- Discriminant validity: features NOT expected to correlate with dimensions SHOULD NOT

Expected convergent relationships:
- section_count <-> A1 (Completeness)
- heading_consistency <-> A2 (Structural Conformance)
- context_word_count <-> B1 (Context Adequacy)
- n_alternatives <-> B2 (Alternatives Coverage)
- rationale_word_count <-> B3 (Rationale Depth)
- n_consequences <-> B4 (Consequence Specificity)
- decision_specificity_score <-> B5 (Decision Specificity)
- readability_score <-> C1 (Clarity and Readability)
- n_references <-> C3 (Traceability)

Usage:
    python scripts/run_rq2_convergent_validity.py --adr-dir adrs/ --scores-dir data/results/rq1/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from adr_analyser.parsing.parser import ParsedADR, parse_adr_directory
from adr_analyser.parsing.section_extractor import extract_sections
from adr_analyser.quality_model.dimensions import DIMENSION_ORDER, QUALITY_MODEL


def extract_objective_features(adr: ParsedADR) -> dict[str, float]:
    """Extract objective, computable features from an ADR.

    Returns a dict of feature_name -> numeric value.
    """
    sections = extract_sections(adr)
    body = adr.body

    # Basic structural features
    features = {
        "word_count": float(adr.word_count),
        "heading_count": float(adr.heading_count),
        "has_code_block": float(adr.has_code_block),
        "mandatory_sections": float(sections.mandatory_sections_present),
        "optional_sections": float(sections.optional_sections_present),
        "total_sections": float(sections.total_sections_present),
    }

    # Heading consistency: are heading levels sequential (no skipping)?
    heading_levels = [h[0] for h in adr.headings]
    if len(heading_levels) > 1:
        level_diffs = [abs(heading_levels[i + 1] - heading_levels[i])
                       for i in range(len(heading_levels) - 1)]
        features["heading_consistency"] = 1.0 - min(1.0, np.mean(level_diffs) / 3.0)
    else:
        features["heading_consistency"] = 0.5  # Unknown

    # Has metadata
    has_status = 1.0 if sections.status else 0.0
    has_date = 1.0 if sections.date else 0.0
    has_deciders = 1.0 if sections.deciders else 0.0
    features["metadata_score"] = (has_status + has_date + has_deciders) / 3.0

    # Context-specific features
    context_text = sections.context or ""
    features["context_word_count"] = float(len(context_text.split()))

    # Count decision drivers/forces in context
    driver_patterns = [r"need\b", r"require\b", r"must\b", r"should\b",
                       r"constraint", r"force", r"driver"]
    driver_count = sum(
        len(re.findall(p, context_text, re.IGNORECASE)) for p in driver_patterns
    )
    features["context_driver_mentions"] = float(driver_count)

    # Alternatives coverage
    decision_text = sections.decision or ""
    options_text = sections.considered_options or ""
    # Count distinct technologies/options mentioned
    features["n_alternatives_mentioned"] = _count_alternatives(
        decision_text + " " + options_text + " " + (sections.rationale or "")
    )

    # Rationale depth
    rationale_text = sections.rationale or ""
    features["rationale_word_count"] = float(len(rationale_text.split()))
    features["has_because_clause"] = float(
        bool(re.search(r"\bbecause\b", rationale_text + " " + decision_text, re.IGNORECASE))
    )

    # Consequence specificity
    consequence_text = (sections.consequences or "") + " " + (sections.pros or "") + " " + (sections.cons or "")
    # Count bullet points as proxy for number of consequences
    features["n_consequences"] = float(
        len(re.findall(r"^[\s]*[-*●○•]\s", consequence_text, re.MULTILINE))
    )
    features["has_pros_and_cons"] = float(
        bool(sections.pros) and bool(sections.cons)
        or bool(re.search(r"\bpros?\b.*\bcons?\b", consequence_text, re.IGNORECASE | re.DOTALL))
    )

    # Decision specificity
    features["decision_word_count"] = float(len(decision_text.split()))
    # Count specific technology names (capitalized words, version numbers)
    features["decision_specific_terms"] = float(
        len(re.findall(r"\b[A-Z][a-zA-Z]+\b", decision_text))
        + len(re.findall(r"\d+\.\d+", decision_text))
    )

    # Readability proxy (average sentence length)
    sentences = re.split(r"[.!?]+", body)
    sentences = [s.strip() for s in sentences if s.strip()]
    if sentences:
        avg_sentence_len = np.mean([len(s.split()) for s in sentences])
        features["avg_sentence_length"] = float(avg_sentence_len)
    else:
        features["avg_sentence_length"] = 0.0

    # Type-token ratio (lexical diversity)
    words = body.lower().split()
    if words:
        features["type_token_ratio"] = float(len(set(words)) / len(words))
    else:
        features["type_token_ratio"] = 0.0

    # Reference/link count
    features["n_references"] = float(
        len(re.findall(r"https?://\S+", body))
        + len(re.findall(r"\[.*?\]\(.*?\)", body))
    )

    return features


def _count_alternatives(text: str) -> float:
    """Count the number of distinct alternatives/options mentioned."""
    # Look for option/alternative listing patterns
    option_patterns = [
        r"option\s+\d",
        r"alternative\s+\d",
        r"^[-*●]\s+\*?\*?(?:Option|Alternative)\b",
    ]
    count = sum(
        len(re.findall(p, text, re.IGNORECASE | re.MULTILINE)) for p in option_patterns
    )

    # Also count distinct technology names in comparison context
    vs_pattern = re.findall(r"\bvs\.?\b|\bversus\b|\bcompared to\b|\binstead of\b",
                            text, re.IGNORECASE)
    count += len(vs_pattern)

    return float(max(count, 1))  # At least 1 (the chosen option)


# Expected convergent correlations: (feature, dimension) pairs that SHOULD correlate
CONVERGENT_HYPOTHESES = {
    ("mandatory_sections", "A1"): "positive",
    ("total_sections", "A1"): "positive",
    ("heading_count", "A2"): "positive",
    ("heading_consistency", "A2"): "positive",
    ("metadata_score", "A2"): "positive",
    ("context_word_count", "B1"): "positive",
    ("context_driver_mentions", "B1"): "positive",
    ("n_alternatives_mentioned", "B2"): "positive",
    ("rationale_word_count", "B3"): "positive",
    ("has_because_clause", "B3"): "positive",
    ("n_consequences", "B4"): "positive",
    ("has_pros_and_cons", "B4"): "positive",
    ("decision_word_count", "B5"): "positive",
    ("decision_specific_terms", "B5"): "positive",
    ("avg_sentence_length", "C1"): "negative",  # Shorter sentences = more readable
    ("type_token_ratio", "C1"): "positive",
    ("n_references", "C3"): "positive",
}

# Discriminant: these should NOT correlate significantly
DISCRIMINANT_HYPOTHESES = {
    ("word_count", "C2"): "null",  # Word count shouldn't predict consistency
    ("heading_count", "B3"): "null",  # Headings shouldn't predict rationale depth
    ("n_references", "B5"): "null",  # References shouldn't predict decision specificity
    ("has_code_block", "C1"): "null",  # Code blocks shouldn't predict clarity
}


def compute_mtmm_matrix(
    features: dict[str, list[float]],
    scores: dict[str, list[int]],
) -> dict:
    """Compute the Multi-Trait Multi-Method style correlation matrix.

    Returns:
        Dict with correlation matrix, convergent/discriminant results.
    """
    feature_names = sorted(features.keys())
    dim_ids = DIMENSION_ORDER

    # Correlation matrix: features × dimensions
    matrix = {}
    for feat in feature_names:
        matrix[feat] = {}
        for dim in dim_ids:
            feat_arr = np.array(features[feat])
            score_arr = np.array(scores[dim])

            if len(feat_arr) < 3 or feat_arr.std() == 0 or score_arr.std() == 0:
                matrix[feat][dim] = {"rho": 0.0, "p": 1.0}
                continue

            rho, p_val = stats.spearmanr(feat_arr, score_arr)
            matrix[feat][dim] = {
                "rho": round(float(rho), 4),
                "p": round(float(p_val), 6),
            }

    # Evaluate convergent hypotheses
    convergent_results = {}
    for (feat, dim), expected_dir in CONVERGENT_HYPOTHESES.items():
        if feat not in matrix:
            continue
        entry = matrix[feat][dim]
        rho = entry["rho"]
        p = entry["p"]
        confirmed = False
        if expected_dir == "positive" and rho > 0 and p < 0.05:
            confirmed = True
        elif expected_dir == "negative" and rho < 0 and p < 0.05:
            confirmed = True
        convergent_results[f"{feat}<->{dim}"] = {
            "expected": expected_dir,
            "rho": rho,
            "p": p,
            "confirmed": confirmed,
        }

    # Evaluate discriminant hypotheses
    discriminant_results = {}
    for (feat, dim), _ in DISCRIMINANT_HYPOTHESES.items():
        if feat not in matrix:
            continue
        entry = matrix[feat][dim]
        rho = entry["rho"]
        p = entry["p"]
        discriminant_results[f"{feat}<->{dim}"] = {
            "rho": rho,
            "p": p,
            "is_null": p > 0.05,  # Confirmed discriminant if NOT significant
        }

    # Summary statistics
    n_convergent_confirmed = sum(1 for v in convergent_results.values() if v["confirmed"])
    n_convergent_total = len(convergent_results)
    n_discriminant_confirmed = sum(1 for v in discriminant_results.values() if v["is_null"])
    n_discriminant_total = len(discriminant_results)

    return {
        "correlation_matrix": matrix,
        "convergent_hypotheses": convergent_results,
        "discriminant_hypotheses": discriminant_results,
        "summary": {
            "convergent_confirmed": n_convergent_confirmed,
            "convergent_total": n_convergent_total,
            "convergent_rate": round(n_convergent_confirmed / max(n_convergent_total, 1), 3),
            "discriminant_confirmed": n_discriminant_confirmed,
            "discriminant_total": n_discriminant_total,
            "discriminant_rate": round(n_discriminant_confirmed / max(n_discriminant_total, 1), 3),
        },
    }


def run_convergent_validity(adr_dir: str, scores_dir: str, output_dir: str) -> None:
    """Run the full RQ2 convergent validity analysis."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Parse ADRs
    adrs = parse_adr_directory(adr_dir)
    print(f"Parsed {len(adrs)} ADRs")

    # Extract features
    print("Extracting objective features...")
    all_features: dict[str, list[float]] = {}
    adr_filenames = []

    for adr in adrs:
        feats = extract_objective_features(adr)
        adr_filenames.append(adr.filename)

        for feat_name, value in feats.items():
            if feat_name not in all_features:
                all_features[feat_name] = []
            all_features[feat_name].append(value)

    # Feature summary statistics
    print(f"\nExtracted {len(all_features)} features for {len(adrs)} ADRs:")
    for feat_name, values in sorted(all_features.items()):
        arr = np.array(values)
        print(f"  {feat_name:30s}: mean={arr.mean():.2f}, std={arr.std():.2f}, "
              f"min={arr.min():.1f}, max={arr.max():.1f}")

    # Save features
    features_data = {}
    for i, filename in enumerate(adr_filenames):
        features_data[filename] = {
            feat: all_features[feat][i] for feat in all_features
        }
    with open(output_path / "objective_features.json", "w") as f:
        json.dump(features_data, f, indent=2)
    print(f"\nFeatures saved to {output_path / 'objective_features.json'}")

    # Load LLM scores (if available)
    scores_path = Path(scores_dir)
    score_files = list(scores_path.glob("scores_*.json"))

    if not score_files:
        print("\nNo score files found. Run RQ1 scoring first.")
        print("Features have been computed and saved. Re-run after scoring.")

        # Still compute correlations with baseline scores for validation
        print("\n=== Computing correlations with non-LLM baselines ===")
        _run_baseline_correlations(adrs, all_features, adr_filenames, output_path)
        return

    # Use first model's scores (or average across models)
    all_model_scores = {}
    for score_file in score_files:
        model_name = score_file.stem.replace("scores_", "")
        with open(score_file) as f:
            all_model_scores[model_name] = json.load(f)

    # For MTMM, use each model separately
    for model_name, model_scores in all_model_scores.items():
        print(f"\n=== Convergent Validity for {model_name} ===")

        # Align features with scores
        common_adrs = [fn for fn in adr_filenames if fn in model_scores]
        if len(common_adrs) < 10:
            print(f"Too few common ADRs ({len(common_adrs)}), skipping {model_name}")
            continue

        aligned_features = {}
        for feat_name in all_features:
            aligned_features[feat_name] = [
                features_data[adr][feat_name] for adr in common_adrs
            ]

        aligned_scores = {}
        for dim_id in DIMENSION_ORDER:
            aligned_scores[dim_id] = [
                model_scores[adr].get(dim_id, 2) for adr in common_adrs
            ]

        # Compute MTMM matrix
        mtmm = compute_mtmm_matrix(aligned_features, aligned_scores)

        # Save per-model results
        with open(output_path / f"rq2_mtmm_{model_name}.json", "w") as f:
            json.dump(mtmm, f, indent=2)

        _print_mtmm_summary(model_name, mtmm)

    print(f"\nAll RQ2 results saved to {output_path}")


def _run_baseline_correlations(
    adrs: list[ParsedADR],
    features: dict[str, list[float]],
    filenames: list[str],
    output_path: Path,
) -> None:
    """Compute correlations between features and non-LLM baseline scores."""
    from adr_analyser.baselines.non_llm import SectionCountBaseline, WordCountBaseline

    section_bl = SectionCountBaseline()
    word_bl = WordCountBaseline()

    # Compute baseline scores
    baseline_scores: dict[str, dict[str, list[int]]] = {
        "section_baseline": {},
        "word_baseline": {},
    }

    for adr in adrs:
        s_scores = section_bl.predict(adr)
        w_scores = word_bl.predict(adr)
        for dim_id in DIMENSION_ORDER:
            if dim_id not in baseline_scores["section_baseline"]:
                baseline_scores["section_baseline"][dim_id] = []
                baseline_scores["word_baseline"][dim_id] = []
            baseline_scores["section_baseline"][dim_id].append(s_scores[dim_id])
            baseline_scores["word_baseline"][dim_id].append(w_scores[dim_id])

    for bl_name, scores in baseline_scores.items():
        mtmm = compute_mtmm_matrix(features, scores)
        with open(output_path / f"rq2_mtmm_{bl_name}.json", "w") as f:
            json.dump(mtmm, f, indent=2)
        _print_mtmm_summary(bl_name, mtmm)


def _print_mtmm_summary(model_name: str, mtmm: dict) -> None:
    """Print MTMM analysis summary."""
    summary = mtmm["summary"]
    print(f"\n  {model_name}:")
    print(f"    Convergent: {summary['convergent_confirmed']}/{summary['convergent_total']} "
          f"({summary['convergent_rate']:.1%}) hypotheses confirmed")
    print(f"    Discriminant: {summary['discriminant_confirmed']}/{summary['discriminant_total']} "
          f"({summary['discriminant_rate']:.1%}) non-correlations confirmed")

    print("    Key convergent results:")
    for key, result in mtmm["convergent_hypotheses"].items():
        marker = "Y" if result["confirmed"] else "N"
        print(f"      [{marker}] {key}: rho={result['rho']:.3f}, p={result['p']:.4f}")


def main():
    parser = argparse.ArgumentParser(description="RQ2: Convergent Validity Experiment")
    parser.add_argument("--adr-dir", default="adrs/", help="ADR directory")
    parser.add_argument("--scores-dir", default="data/results/rq1/",
                        help="Directory with model score files")
    parser.add_argument("--output-dir", default="data/results/rq2/", help="Output directory")

    args = parser.parse_args()
    run_convergent_validity(args.adr_dir, args.scores_dir, args.output_dir)


if __name__ == "__main__":
    main()
