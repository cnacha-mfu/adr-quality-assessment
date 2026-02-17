#!/usr/bin/env python3
"""
RQ3: Perturbation Sensitivity Experiment

Research Question: Can LLM scorers detect controlled quality degradations
in the correct quality dimensions?

Approach:
1. Select ADR candidates suitable for perturbation (sufficient sections, word count)
2. Apply 10 systematic perturbation types to each candidate
3. Score both original and perturbed ADRs with LLM scorer
4. Verify that:
   a) The targeted dimension score decreases (or increases for enhancements)
   b) Non-targeted dimensions remain stable
5. Statistical analysis:
   - Paired Wilcoxon signed-rank test (original vs. perturbed per dimension)
   - Cliff's delta effect size
   - Sensitivity = % of perturbations correctly detected
   - Specificity = % of non-targeted dimensions correctly unchanged

This is the KEY validation: if LLM scorers can detect controlled degradations
in the right dimensions, it provides strong evidence of construct validity
WITHOUT requiring human annotation.

Usage:
    # Step 1: Generate perturbed ADRs and batch input
    python scripts/run_rq3_perturbation.py --generate --adr-dir adrs/

    # Step 2: Score online with each model (parallel-safe, checkpoint/resume)
    python scripts/run_rq3_perturbation.py --online --models gemini-2.5-flash
    python scripts/run_rq3_perturbation.py --online --models llama-4-scout
    python scripts/run_rq3_perturbation.py --online --models gpt-oss-20b
    python scripts/run_rq3_perturbation.py --online --models nemotron-nano-30b

    # Step 3: Analyze results (reads all perturbation_scores_*.json)
    python scripts/run_rq3_perturbation.py --analyze --output-dir data/results/rq3/
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def _load_dotenv():
    """Load .env file from project root if it exists."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()

from adr_analyser.evaluation.comparison import compute_cliffs_delta
from adr_analyser.parsing.parser import parse_adr_directory
from adr_analyser.perturbation.generator import (
    PerturbationType,
    generate_all_perturbations,
    select_perturbation_candidates,
)
from adr_analyser.quality_model.dimensions import DIMENSION_ORDER, QUALITY_MODEL
from adr_analyser.scoring.gemini_scorer import GeminiScorer, ADRAssessment
from adr_analyser.scoring.vllm_scorer import VLLMScorer


# ---------------------------------------------------------------------------
# Model configurations (same as RQ1, but with 3 passes for perturbation)
# ---------------------------------------------------------------------------
MODEL_CONFIGS = {
    "gemini-2.5-flash": {
        "class": "GeminiScorer",
        "model_name": "gemini-2.5-flash",
        "temperature": 0.0,
        "num_passes": 3,
        "rate_limit": {"rpm": 500, "rpd": None},
    },
    "llama-4-scout": {
        "class": "VLLMScorer",
        "model_name": "meta/llama-4-scout-17b-16e-instruct",
        "api_base": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY",
        "temperature": 0.0,
        "num_passes": 3,
        "max_tokens": 2048,
        "rate_limit": {"rpm": 40, "rpd": None},
    },
    "gpt-oss-20b": {
        "class": "VLLMScorer",
        "model_name": "openai/gpt-oss-20b",
        "api_base": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY_3",
        "temperature": 0.0,
        "num_passes": 3,
        "max_tokens": 2048,
        "rate_limit": {"rpm": 40, "rpd": None},
    },
    "nemotron-nano-30b": {
        "class": "VLLMScorer",
        "model_name": "nvidia/nemotron-3-nano-30b-a3b",
        "api_base": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY_2",
        "temperature": 0.0,
        "num_passes": 3,
        "max_tokens": 2048,
        "rate_limit": {"rpm": 40, "rpd": None},
    },
}


def _create_scorer(config: dict):
    """Instantiate the appropriate scorer from a MODEL_CONFIGS entry."""
    if config["class"] == "GeminiScorer":
        return GeminiScorer(
            model_name=config["model_name"],
            temperature=config["temperature"],
            num_passes=config["num_passes"],
        )
    elif config["class"] == "VLLMScorer":
        api_key_env = config.get("api_key_env", "")
        api_key = os.environ.get(api_key_env, "EMPTY")
        return VLLMScorer(
            model_name=config["model_name"],
            api_base=config.get("api_base", "http://localhost:8000/v1"),
            api_key=api_key,
            temperature=config["temperature"],
            num_passes=config["num_passes"],
            max_tokens=config.get("max_tokens", 2048),
        )
    else:
        raise ValueError(f"Unknown scorer class: {config['class']}")


def _log(model_key: str, msg: str) -> None:
    """Print a log line with timestamp and model prefix."""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [rq3/{model_key}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Step 1: Generate perturbation dataset
# ---------------------------------------------------------------------------

def generate_perturbation_dataset(adr_dir: str, output_dir: str) -> None:
    """Generate the complete perturbation dataset and batch scoring input."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Parse ADRs
    adrs = parse_adr_directory(adr_dir)
    print(f"Parsed {len(adrs)} ADRs from {adr_dir}")

    # Select candidates
    candidates = select_perturbation_candidates(adrs, min_sections=2, min_word_count=150)
    print(f"Selected {len(candidates)} ADRs suitable for perturbation")

    # Generate perturbations
    perturbation_manifest = {
        "n_originals": len(candidates),
        "perturbation_types": [pt.value for pt in PerturbationType],
        "entries": [],
    }

    all_scoring_pairs = []  # (id, content) for batch scoring

    for adr in candidates:
        pset = generate_all_perturbations(adr)

        # Add original for scoring
        orig_id = f"original__{adr.filename}"
        all_scoring_pairs.append((orig_id, adr.raw_content))

        for perturbed in pset.perturbations:
            pert_id = f"{perturbed.perturbation_type.value}__{adr.filename}"
            all_scoring_pairs.append((pert_id, perturbed.perturbed_content))

            perturbation_manifest["entries"].append({
                "original_filename": adr.filename,
                "perturbation_type": perturbed.perturbation_type.value,
                "perturbation_id": pert_id,
                "original_id": orig_id,
                "description": perturbed.description,
                "expected_impacts": perturbed.expected_dimension_impacts,
                "sections_modified": perturbed.sections_modified,
            })

    # Save manifest
    with open(output_path / "perturbation_manifest.json", "w") as f:
        json.dump(perturbation_manifest, f, indent=2)
    print(f"Manifest saved: {len(perturbation_manifest['entries'])} perturbations "
          f"from {len(candidates)} ADRs")

    # Save perturbed content for inspection
    perturbed_dir = output_path / "perturbed_adrs"
    perturbed_dir.mkdir(exist_ok=True)

    for scoring_id, content in all_scoring_pairs:
        safe_name = scoring_id.replace("/", "_").replace(" ", "_")
        with open(perturbed_dir / f"{safe_name}.md", "w", encoding="utf-8") as f:
            f.write(content)

    print(f"\nGenerated files:")
    print(f"  Manifest: {output_path / 'perturbation_manifest.json'}")
    print(f"  Perturbed ADRs: {perturbed_dir}/ ({len(all_scoring_pairs)} files)")
    print(f"\nTotal items to score: {len(all_scoring_pairs)}")


# ---------------------------------------------------------------------------
# Step 2: Online scoring (rate-limited, checkpoint/resume)
# ---------------------------------------------------------------------------

def score_perturbations_online(
    output_dir: str, models: list[str] | None = None,
) -> None:
    """Score all perturbed + original ADRs via API with checkpoint/resume."""
    output_path = Path(output_dir)
    perturbed_dir = output_path / "perturbed_adrs"

    # Load manifest to get list of scoring IDs
    manifest_file = output_path / "perturbation_manifest.json"
    if not manifest_file.exists():
        print("Error: perturbation_manifest.json not found. Run --generate first.")
        return

    with open(manifest_file) as f:
        manifest = json.load(f)

    # Build scoring pairs from perturbed_adrs/ directory
    scoring_pairs = []
    # Originals
    seen_originals = set()
    for entry in manifest["entries"]:
        orig_id = entry["original_id"]
        if orig_id not in seen_originals:
            seen_originals.add(orig_id)
            safe_name = orig_id.replace("/", "_").replace(" ", "_")
            content_file = perturbed_dir / f"{safe_name}.md"
            if content_file.exists():
                scoring_pairs.append((orig_id, content_file.read_text(encoding="utf-8")))
    # Perturbations
    for entry in manifest["entries"]:
        pert_id = entry["perturbation_id"]
        safe_name = pert_id.replace("/", "_").replace(" ", "_")
        content_file = perturbed_dir / f"{safe_name}.md"
        if content_file.exists():
            scoring_pairs.append((pert_id, content_file.read_text(encoding="utf-8")))

    print(f"Loaded {len(scoring_pairs)} items to score")

    configs = {
        k: v for k, v in MODEL_CONFIGS.items()
        if models is None or k in models
    }

    if not configs:
        print("No models selected. Use --models with valid model keys.")
        print(f"Available: {list(MODEL_CONFIGS.keys())}")
        return

    for model_key, config in configs.items():
        safe_name = model_key.replace("/", "_")
        scores_file = output_path / f"perturbation_scores_{safe_name}.json"

        # Load checkpoint
        all_scores = {}
        if scores_file.exists():
            with open(scores_file) as f:
                all_scores = json.load(f)

        # Check API key
        api_key_env = config.get("api_key_env", "")
        if api_key_env and not os.environ.get(api_key_env):
            _log(model_key, f"ERROR: env var {api_key_env} not set — skipping")
            continue

        scorer = _create_scorer(config)
        rate_limit = config.get("rate_limit", {})
        rpm = rate_limit.get("rpm", 30)
        min_delay = 60.0 / rpm + 0.1
        # Concurrency: use up to rpm/6 workers (burst within a 10s window)
        max_concurrent = max(2, min(30, rpm // 6))

        scored = 0
        skipped = 0

        _log(model_key, f"START — {config['model_name']}, {rpm} RPM, "
             f"{max_concurrent} concurrent, "
             f"checkpoint: {len(all_scores)}/{len(scoring_pairs)} items")

        for scoring_id, content in scoring_pairs:
            if scoring_id in all_scores:
                skipped += 1
                continue

            _log(model_key, f"[{skipped + scored + 1}/{len(scoring_pairs)}] {scoring_id}")

            try:
                assessment = _score_item_rate_limited(
                    scorer, model_key, content, scoring_id, min_delay,
                    max_concurrent=max_concurrent,
                )
            except Exception as e:
                _log(model_key, f"ERROR: {e} — saving checkpoint and stopping.")
                break

            all_scores[scoring_id] = assessment.median_scores
            scored += 1

            # Checkpoint after each item
            with open(scores_file, "w") as f:
                json.dump(all_scores, f, indent=2)

            remaining = len(scoring_pairs) - scored - skipped
            _log(model_key, f"  done — {scored} scored, {remaining} remaining")

        _log(model_key, f"FINISH — {scored} new, {len(all_scores)} total")


def _score_item_rate_limited(
    scorer,
    model_key: str,
    content: str,
    item_id: str,
    min_delay: float,
    max_concurrent: int = 10,
) -> ADRAssessment:
    """Score a single item with concurrent API calls and rate limiting.

    Fires up to max_concurrent calls in parallel using a thread pool,
    with a token-bucket rate limiter to respect RPM limits.
    """
    dims = DIMENSION_ORDER
    assessment = ADRAssessment(
        adr_filename=item_id,
        adr_content=content,
        dimension_scores={d: [] for d in dims},
    )

    total_calls = scorer.num_passes * len(dims)
    rate_lock = threading.Lock()
    last_call_time = [0.0]  # mutable container for closure
    completed = [0]

    def _rate_limited_score(pass_num, dim_id):
        """Score one dimension/pass with rate limiting and retries."""
        # Rate limit: ensure min_delay between consecutive calls
        with rate_lock:
            now = time.monotonic()
            wait = min_delay - (now - last_call_time[0])
            if wait > 0:
                time.sleep(wait)
            last_call_time[0] = time.monotonic()

        for attempt in range(4):
            try:
                score = scorer.score_dimension(content, dim_id, pass_num)
                with rate_lock:
                    completed[0] += 1
                    n = completed[0]
                _log(model_key, f"  [{n}/{total_calls}] p{pass_num} {dim_id}={score.score}")
                return pass_num, dim_id, score
            except Exception as e:
                err_str = str(e).lower()
                if "tokens per day" in err_str or "token_quota_exceeded" in err_str:
                    raise
                backoff = min_delay * (2 ** attempt) + 5
                if attempt < 3:
                    _log(model_key, f"  RETRY {attempt+1}/3 {dim_id}/p{pass_num}: {e} (wait {backoff:.0f}s)")
                    time.sleep(backoff)
                else:
                    raise

    # Build all (pass_num, dim_id) tasks
    tasks = [
        (pass_num, dim_id)
        for pass_num in range(1, scorer.num_passes + 1)
        for dim_id in dims
    ]

    start = time.monotonic()
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        futures = {
            executor.submit(_rate_limited_score, pn, did): (pn, did)
            for pn, did in tasks
        }
        for future in as_completed(futures):
            pass_num, dim_id, score = future.result()
            assessment.dimension_scores[dim_id].append(score)

    elapsed = time.monotonic() - start
    _log(model_key, f"  {total_calls} calls in {elapsed:.1f}s ({total_calls/elapsed:.1f} calls/s)")

    return assessment


# ---------------------------------------------------------------------------
# Step 3: Analyze results
# ---------------------------------------------------------------------------

def analyze_perturbation_results(output_dir: str) -> None:
    """Analyze the perturbation experiment results.

    Reads perturbation_scores_<model>.json for each model and produces
    per-model and aggregated analysis.
    """
    output_path = Path(output_dir)

    # Load manifest
    with open(output_path / "perturbation_manifest.json") as f:
        manifest = json.load(f)

    # Load scores from all models
    score_files = sorted(output_path.glob("perturbation_scores_*.json"))
    if not score_files:
        # Fallback: legacy single-file format
        legacy = output_path / "perturbation_scores.json"
        if legacy.exists():
            score_files = [legacy]

    if not score_files:
        print("Error: No perturbation_scores_*.json found. Run --online first.")
        return

    all_model_scores = {}
    for sf in score_files:
        model_name = sf.stem.replace("perturbation_scores_", "")
        with open(sf) as f:
            all_model_scores[model_name] = json.load(f)
        print(f"Loaded scores for {model_name}: {len(all_model_scores[model_name])} items")

    print(f"\nLoaded {len(manifest['entries'])} perturbation entries")

    # Analyze per model
    full_results = {"per_model": {}}

    for model_name, all_scores in all_model_scores.items():
        print(f"\n{'=' * 60}")
        print(f"Analyzing model: {model_name}")
        print(f"{'=' * 60}")

        results = {
            "per_perturbation_type": {},
            "per_dimension": {},
            "overall": {},
        }

        for ptype_str in manifest["perturbation_types"]:
            ptype = PerturbationType(ptype_str)
            entries = [e for e in manifest["entries"] if e["perturbation_type"] == ptype_str]
            if not entries:
                continue
            type_results = _analyze_perturbation_type(ptype, entries, all_scores)
            results["per_perturbation_type"][ptype_str] = type_results

        for dim_id in DIMENSION_ORDER:
            dim_sensitivity = _compute_dimension_sensitivity(dim_id, manifest, all_scores)
            results["per_dimension"][dim_id] = dim_sensitivity

        results["overall"] = _compute_overall_summary(results)
        full_results["per_model"][model_name] = results

        _print_summary(results, model_name)

    # Save results
    with open(output_path / "rq3_results.json", "w") as f:
        json.dump(full_results, f, indent=2)

    _generate_paper_table(full_results, output_path)


def _analyze_perturbation_type(
    ptype: PerturbationType,
    entries: list[dict],
    all_scores: dict,
) -> dict:
    """Analyze results for a single perturbation type."""
    paired_scores = {dim_id: {"original": [], "perturbed": []} for dim_id in DIMENSION_ORDER}

    for entry in entries:
        orig_id = entry["original_id"]
        pert_id = entry["perturbation_id"]

        if orig_id not in all_scores or pert_id not in all_scores:
            continue

        for dim_id in DIMENSION_ORDER:
            orig_score = all_scores[orig_id].get(dim_id, 2)
            pert_score = all_scores[pert_id].get(dim_id, 2)
            paired_scores[dim_id]["original"].append(orig_score)
            paired_scores[dim_id]["perturbed"].append(pert_score)

    expected_impacts = entries[0]["expected_impacts"] if entries else {}

    dim_results = {}
    for dim_id in DIMENSION_ORDER:
        orig = np.array(paired_scores[dim_id]["original"])
        pert = np.array(paired_scores[dim_id]["perturbed"])
        n = len(orig)

        if n < 3:
            dim_results[dim_id] = {"n": n, "error": "insufficient_data"}
            continue

        try:
            w_stat, p_val = stats.wilcoxon(orig, pert, alternative="two-sided")
        except ValueError:
            w_stat, p_val = 0.0, 1.0

        delta = compute_cliffs_delta(orig, pert, n_bootstrap=5000)
        mean_diff = float((orig - pert).mean())

        expected = expected_impacts.get(dim_id, "unchanged")
        if expected == "decrease":
            detected = float((orig > pert).sum() / n)
        elif expected == "increase":
            detected = float((pert > orig).sum() / n)
        else:
            detected = float((orig == pert).sum() / n)

        dim_results[dim_id] = {
            "n": n,
            "expected_impact": expected,
            "original_mean": round(float(orig.mean()), 3),
            "perturbed_mean": round(float(pert.mean()), 3),
            "mean_difference": round(mean_diff, 3),
            "wilcoxon_w": round(float(w_stat), 4),
            "p_value": round(float(p_val), 6),
            "cliffs_delta": delta.delta,
            "cliffs_delta_ci": [delta.ci_lower, delta.ci_upper],
            "cliffs_interpretation": delta.interpretation,
            "detection_rate": round(detected, 3),
            "significant": p_val < 0.05,
        }

    return {
        "n_entries": len(entries),
        "perturbation_description": entries[0]["description"] if entries else "",
        "expected_impacts": expected_impacts,
        "dimension_results": dim_results,
    }


def _compute_dimension_sensitivity(
    dim_id: str,
    manifest: dict,
    all_scores: dict,
) -> dict:
    """Compute overall sensitivity/specificity for a single dimension."""
    true_positives = 0
    false_negatives = 0
    true_negatives = 0
    false_positives = 0

    for entry in manifest["entries"]:
        orig_id = entry["original_id"]
        pert_id = entry["perturbation_id"]

        if orig_id not in all_scores or pert_id not in all_scores:
            continue

        orig_score = all_scores[orig_id].get(dim_id, 2)
        pert_score = all_scores[pert_id].get(dim_id, 2)
        expected = entry["expected_impacts"].get(dim_id, "unchanged")

        if expected == "decrease":
            if pert_score < orig_score:
                true_positives += 1
            else:
                false_negatives += 1
        elif expected == "increase":
            if pert_score > orig_score:
                true_positives += 1
            else:
                false_negatives += 1
        else:
            if pert_score == orig_score:
                true_negatives += 1
            else:
                false_positives += 1

    total_expected_change = true_positives + false_negatives
    total_expected_unchanged = true_negatives + false_positives

    sensitivity = (
        true_positives / total_expected_change if total_expected_change > 0 else 0.0
    )
    specificity = (
        true_negatives / total_expected_unchanged if total_expected_unchanged > 0 else 0.0
    )

    return {
        "dimension_name": QUALITY_MODEL[dim_id].name,
        "true_positives": true_positives,
        "false_negatives": false_negatives,
        "true_negatives": true_negatives,
        "false_positives": false_positives,
        "sensitivity": round(sensitivity, 3),
        "specificity": round(specificity, 3),
        "n_expected_changes": total_expected_change,
        "n_expected_unchanged": total_expected_unchanged,
    }


def _compute_overall_summary(results: dict) -> dict:
    """Compute overall summary statistics."""
    all_sensitivities = []
    all_specificities = []

    for dim_id, dim_data in results["per_dimension"].items():
        if dim_data["n_expected_changes"] > 0:
            all_sensitivities.append(dim_data["sensitivity"])
        if dim_data["n_expected_unchanged"] > 0:
            all_specificities.append(dim_data["specificity"])

    n_significant = 0
    n_total = 0
    for ptype, pdata in results["per_perturbation_type"].items():
        for dim_id, dim_result in pdata["dimension_results"].items():
            if isinstance(dim_result, dict) and "significant" in dim_result:
                n_total += 1
                if dim_result["significant"]:
                    n_significant += 1

    return {
        "mean_sensitivity": round(float(np.mean(all_sensitivities)), 3) if all_sensitivities else 0.0,
        "mean_specificity": round(float(np.mean(all_specificities)), 3) if all_specificities else 0.0,
        "n_significant_effects": n_significant,
        "n_total_tests": n_total,
        "significant_rate": round(n_significant / max(n_total, 1), 3),
    }


def _generate_paper_table(full_results: dict, output_path: Path) -> None:
    """Generate paper-ready table for RQ3."""
    lines = [
        "# RQ3: Perturbation Sensitivity Results\n",
    ]

    for model_name, results in full_results["per_model"].items():
        lines.append(f"## Model: {model_name}\n")
        lines.append("### Per-Dimension Sensitivity and Specificity\n")
        lines.append("| Dimension | Sensitivity | Specificity | TP | FN | TN | FP |")
        lines.append("|-----------|:----------:|:----------:|:--:|:--:|:--:|:--:|")

        for dim_id in DIMENSION_ORDER:
            dim_data = results["per_dimension"].get(dim_id, {})
            name = QUALITY_MODEL[dim_id].name
            sens = dim_data.get("sensitivity", 0)
            spec = dim_data.get("specificity", 0)
            tp = dim_data.get("true_positives", 0)
            fn = dim_data.get("false_negatives", 0)
            tn = dim_data.get("true_negatives", 0)
            fp = dim_data.get("false_positives", 0)
            lines.append(f"| {dim_id} {name} | {sens:.3f} | {spec:.3f} | {tp} | {fn} | {tn} | {fp} |")

        summary = results.get("overall", {})
        lines.append(f"| **Mean** | **{summary.get('mean_sensitivity', 0):.3f}** | "
                     f"**{summary.get('mean_specificity', 0):.3f}** | — | — | — | — |")
        lines.append("")

    with open(output_path / "rq3_perturbation_table.md", "w") as f:
        f.write("\n".join(lines))
    print(f"Paper table saved to {output_path / 'rq3_perturbation_table.md'}")


def _print_summary(results: dict, model_name: str) -> None:
    """Print experiment summary to console."""
    print(f"\n{'=' * 70}")
    print(f"RQ3 SUMMARY: Perturbation Sensitivity — {model_name}")
    print("=" * 70)

    summary = results.get("overall", {})
    print(f"  Mean sensitivity: {summary.get('mean_sensitivity', 0):.3f}")
    print(f"  Mean specificity: {summary.get('mean_specificity', 0):.3f}")
    print(f"  Significant effects: {summary.get('n_significant_effects', 0)}"
          f"/{summary.get('n_total_tests', 0)}")

    print("\n  Per-dimension:")
    for dim_id in DIMENSION_ORDER:
        dim_data = results["per_dimension"].get(dim_id, {})
        name = QUALITY_MODEL[dim_id].name
        sens = dim_data.get("sensitivity", 0)
        spec = dim_data.get("specificity", 0)
        print(f"    {dim_id} {name:30s} sens={sens:.3f} spec={spec:.3f}")


def main():
    parser = argparse.ArgumentParser(description="RQ3: Perturbation Sensitivity Experiment")
    parser.add_argument("--adr-dir", default="adrs/", help="ADR directory")
    parser.add_argument("--output-dir", default="data/results/rq3/", help="Output directory")
    parser.add_argument("--generate", action="store_true",
                        help="Generate perturbation dataset")
    parser.add_argument("--online", action="store_true",
                        help="Score perturbations online via API (rate-limited, checkpoint/resume)")
    parser.add_argument("--models", nargs="*", default=None,
                        help="Specific model keys to score with (default: all)")
    parser.add_argument("--analyze", action="store_true",
                        help="Analyze perturbation scoring results")

    args = parser.parse_args()

    if args.generate:
        generate_perturbation_dataset(args.adr_dir, args.output_dir)
    elif args.online:
        score_perturbations_online(args.output_dir, args.models)
    elif args.analyze:
        analyze_perturbation_results(args.output_dir)
    else:
        print("RQ3: Perturbation Sensitivity Experiment\n")
        print("Available models:")
        for key, cfg in MODEL_CONFIGS.items():
            print(f"  {key:40s} ({cfg['class']})")
        print()
        print("Usage:")
        print("  Step 1: Generate perturbations:")
        print("    python scripts/run_rq3_perturbation.py --generate")
        print("  Step 2: Score online (per model, checkpoint/resume):")
        print("    python scripts/run_rq3_perturbation.py --online --models gemini-2.5-flash")
        print("    python scripts/run_rq3_perturbation.py --online --models llama-4-scout")
        print("  Step 3: Analyze results:")
        print("    python scripts/run_rq3_perturbation.py --analyze")


if __name__ == "__main__":
    main()
