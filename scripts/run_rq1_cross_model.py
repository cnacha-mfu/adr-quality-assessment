#!/usr/bin/env python3
"""
RQ1: Cross-Model Agreement Experiment

Research Question: To what extent do different LLMs agree when assessing
ADR quality on the same rubric?

Approach:
- Score all 109 ADRs with 4 LLM "raters" from 4 model families / 2 providers
  - Gemini 2.5 Flash (Google Gemini API)
  - Llama 4 Scout 17B (Meta, via NVIDIA NIM)
  - GPT-OSS 20B (OpenAI, via NVIDIA NIM)
  - Nemotron Nano 30B (NVIDIA, via NVIDIA NIM)
- Each model scores every ADR on all 10 dimensions (5 passes each)
- Compute pairwise agreement: QWK, Spearman rho, ICC(2,1)
- Compute multi-rater: Krippendorff's alpha (ordinal)
- Compare model agreement against known inter-annotator agreement benchmarks

Usage:
    # Score online with rate limiting (all models use checkpoint/resume)
    python scripts/run_rq1_cross_model.py --online --models llama-4-scout
    python scripts/run_rq1_cross_model.py --online --models gpt-oss-20b
    python scripts/run_rq1_cross_model.py --online --models nemotron-nano-30b
    # Generate batch JSONL (for Vertex AI or self-hosted vLLM)
    python scripts/run_rq1_cross_model.py --batch-input --models gemini-2.5-flash
    # Analyze all results
    python scripts/run_rq1_cross_model.py --batch-output
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# Add project root to path
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

from adr_analyser.evaluation.agreement import compute_agreement, compute_qwk, compute_icc_21
from adr_analyser.evaluation.comparison import compare_models, compute_cliffs_delta
from adr_analyser.evaluation.irr import krippendorff_alpha_ordinal
from adr_analyser.parsing.parser import parse_adr_directory
from adr_analyser.quality_model.dimensions import DIMENSION_ORDER, QUALITY_MODEL
from adr_analyser.scoring.gemini_scorer import GeminiScorer, ADRAssessment
from adr_analyser.scoring.vllm_scorer import VLLMScorer


# Model configurations for the experiment
# 4 models from 4 distinct families / 2 providers for cross-model agreement
MODEL_CONFIGS = {
    # --- Google Gemini (proprietary) ---
    "gemini-2.5-flash": {
        "class": "GeminiScorer",
        "model_name": "gemini-2.5-flash",
        "temperature": 0.0,
        "num_passes": 5,
        "rate_limit": {"rpm": 500, "rpd": None},
    },
    # --- Meta Llama (open-source, via NVIDIA NIM) ---
    "llama-4-scout": {
        "class": "VLLMScorer",
        "model_name": "meta/llama-4-scout-17b-16e-instruct",
        "api_base": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY",
        "temperature": 0.0,
        "num_passes": 5,
        "max_tokens": 2048,
        "rate_limit": {"rpm": 40, "rpd": None},
    },
    # --- OpenAI GPT-OSS (open-source, via NVIDIA NIM) ---
    "gpt-oss-20b": {
        "class": "VLLMScorer",
        "model_name": "openai/gpt-oss-20b",
        "api_base": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY_3",
        "temperature": 0.0,
        "num_passes": 5,
        "max_tokens": 2048,
        "rate_limit": {"rpm": 40, "rpd": None},
    },
    # --- NVIDIA Nemotron Nano 30B (NVIDIA, via NVIDIA NIM) ---
    "nemotron-nano-30b": {
        "class": "VLLMScorer",
        "model_name": "nvidia/nemotron-3-nano-30b-a3b",
        "api_base": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY_2",
        "temperature": 0.0,
        "num_passes": 5,
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
            supports_system_role=config.get("supports_system_role", True),
        )
    else:
        raise ValueError(f"Unknown scorer class: {config['class']}")


def generate_batch_inputs(
    adr_dir: str, output_dir: str, models: list[str] | None = None,
) -> None:
    """Generate batch JSONL input files for each model."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    adrs = parse_adr_directory(adr_dir)
    print(f"Parsed {len(adrs)} ADRs from {adr_dir}")

    adr_pairs = [(a.filename, a.raw_content) for a in adrs]

    configs = {k: v for k, v in MODEL_CONFIGS.items() if models is None or k in models}

    for model_name, config in configs.items():
        scorer = _create_scorer(config)
        safe_name = model_name.replace("/", "_")
        jsonl_path = output_path / f"batch_input_{safe_name}.jsonl"
        scorer.generate_batch_input(adr_pairs, jsonl_path)
        print(f"Generated batch input for {model_name}: {jsonl_path}")


def load_scores_from_json(scores_dir: str) -> dict[str, dict[str, dict[str, int]]]:
    """Load model scores from JSON result files.

    Expected format per model file:
    {
        "adr_filename.md": {
            "A1": 3,   # median score across passes
            "A2": 2,
            ...
        }
    }

    Returns:
        Dict mapping model_name -> adr_filename -> dim_id -> score.
    """
    scores_dir = Path(scores_dir)
    all_scores = {}

    for score_file in sorted(scores_dir.glob("scores_*.json")):
        model_name = score_file.stem.replace("scores_", "")
        with open(score_file) as f:
            all_scores[model_name] = json.load(f)
        print(f"Loaded scores for {model_name}: {len(all_scores[model_name])} ADRs")

    return all_scores


def compute_pairwise_agreement(
    all_scores: dict[str, dict[str, dict[str, int]]],
) -> dict:
    """Compute pairwise agreement between all model pairs across all dimensions.

    Returns:
        Dict with per-dimension and overall pairwise agreement metrics.
    """
    model_names = sorted(all_scores.keys())
    if len(model_names) < 2:
        print("Error: Need at least 2 models for pairwise comparison")
        return {}

    # Find common ADRs across all models
    common_adrs = set.intersection(
        *[set(all_scores[m].keys()) for m in model_names]
    )
    common_adrs = sorted(common_adrs)
    print(f"Common ADRs across all models: {len(common_adrs)}")

    results = {
        "n_adrs": len(common_adrs),
        "models": model_names,
        "per_dimension": {},
        "overall": {},
    }

    # Per-dimension pairwise agreement
    n_pairs = len(model_names) * (len(model_names) - 1) // 2
    for dim_idx, dim_id in enumerate(DIMENSION_ORDER):
        print(f"  [{dim_idx+1}/{len(DIMENSION_ORDER)}] {dim_id} {QUALITY_MODEL[dim_id].name} "
              f"({n_pairs} pairs)...")
        dim_results = {"pairs": {}}

        for i, m_a in enumerate(model_names):
            for m_b in model_names[i + 1:]:
                scores_a = [all_scores[m_a][adr].get(dim_id, 2) for adr in common_adrs]
                scores_b = [all_scores[m_b][adr].get(dim_id, 2) for adr in common_adrs]

                agreement = compute_agreement(scores_a, scores_b, dim_id)
                pair_key = f"{m_a}_vs_{m_b}"
                dim_results["pairs"][pair_key] = {
                    "qwk": agreement.qwk,
                    "spearman_rho": agreement.spearman_rho,
                    "spearman_p": agreement.spearman_p,
                    "icc_21": agreement.icc_21,
                    "icc_95_ci": list(agreement.icc_95_ci),
                    "mae": agreement.mae,
                    "exact_agreement": agreement.exact_agreement,
                    "adjacent_agreement": agreement.adjacent_agreement,
                }

        # Multi-rater Krippendorff's alpha for this dimension
        reliability_matrix = []
        for m in model_names:
            reliability_matrix.append(
                [all_scores[m][adr].get(dim_id, 2) for adr in common_adrs]
            )

        try:
            alpha = krippendorff_alpha_ordinal(reliability_matrix)
        except Exception:
            alpha = 0.0

        dim_results["krippendorff_alpha"] = round(float(alpha), 4)
        results["per_dimension"][dim_id] = dim_results

    # Overall composite agreement (mean across dimensions)
    print(f"  [Overall] Computing composite agreement ({n_pairs} pairs)...")
    for i, m_a in enumerate(model_names):
        for m_b in model_names[i + 1:]:
            # Compute composite scores (mean across dimensions)
            composite_a = []
            composite_b = []
            for adr in common_adrs:
                mean_a = np.mean([all_scores[m_a][adr].get(d, 2) for d in DIMENSION_ORDER])
                mean_b = np.mean([all_scores[m_b][adr].get(d, 2) for d in DIMENSION_ORDER])
                composite_a.append(round(mean_a))
                composite_b.append(round(mean_b))

            agreement = compute_agreement(composite_a, composite_b, "overall")
            pair_key = f"{m_a}_vs_{m_b}"
            results["overall"][pair_key] = {
                "qwk": agreement.qwk,
                "spearman_rho": agreement.spearman_rho,
                "icc_21": agreement.icc_21,
                "mae": agreement.mae,
                "exact_agreement": agreement.exact_agreement,
                "adjacent_agreement": agreement.adjacent_agreement,
            }

    return results


def compute_score_distributions(
    all_scores: dict[str, dict[str, dict[str, int]]],
) -> dict:
    """Compute score distribution statistics per model per dimension."""
    model_names = sorted(all_scores.keys())
    common_adrs = sorted(
        set.intersection(*[set(all_scores[m].keys()) for m in model_names])
    )

    distributions = {}
    for model_name in model_names:
        distributions[model_name] = {}
        for dim_id in DIMENSION_ORDER:
            scores = [all_scores[model_name][adr].get(dim_id, 2) for adr in common_adrs]
            arr = np.array(scores)
            distributions[model_name][dim_id] = {
                "mean": round(float(arr.mean()), 3),
                "std": round(float(arr.std()), 3),
                "median": round(float(np.median(arr)), 1),
                "score_counts": {
                    str(s): int((arr == s).sum()) for s in range(1, 5)
                },
            }
    return distributions


def generate_paper_tables(results: dict, output_dir: str) -> None:
    """Generate paper-ready tables from RQ1 results."""
    output_path = Path(output_dir)

    # Table: Pairwise agreement per dimension
    lines = [
        "# RQ1: Cross-Model Agreement Results\n",
        "## Pairwise Agreement (QWK) Per Dimension\n",
        "| Dimension | " + " | ".join(
            p for p in results.get("per_dimension", {}).get("A1", {}).get("pairs", {}).keys()
        ) + " | Kripp. alpha |",
        "|-----------|" + "|".join(
            ":---------:" for _ in results.get("per_dimension", {}).get("A1", {}).get("pairs", {})
        ) + "|:-----------:|",
    ]

    for dim_id in DIMENSION_ORDER:
        dim_data = results.get("per_dimension", {}).get(dim_id, {})
        pairs = dim_data.get("pairs", {})
        row = f"| {dim_id} {QUALITY_MODEL[dim_id].name} |"
        for pair_key, metrics in pairs.items():
            row += f" {metrics['qwk']:.3f} |"
        row += f" {dim_data.get('krippendorff_alpha', 0):.3f} |"
        lines.append(row)

    # Overall row
    overall = results.get("overall", {})
    if overall:
        row = "| **Overall** |"
        for pair_key, metrics in overall.items():
            row += f" **{metrics['qwk']:.3f}** |"
        row += " — |"
        lines.append(row)

    lines.append("")
    lines.append("## Interpretation Benchmarks")
    lines.append("| QWK Range | Interpretation |")
    lines.append("|-----------|---------------|")
    lines.append("| 0.81-1.00 | Almost perfect |")
    lines.append("| 0.61-0.80 | Substantial |")
    lines.append("| 0.41-0.60 | Moderate |")
    lines.append("| 0.21-0.40 | Fair |")
    lines.append("| 0.00-0.20 | Slight |")

    with open(output_path / "rq1_agreement_table.md", "w") as f:
        f.write("\n".join(lines))

    print(f"Paper table written to {output_path / 'rq1_agreement_table.md'}")


def analyze_results(output_dir: str) -> None:
    """Main analysis: load scores and compute all RQ1 metrics."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load model scores
    all_scores = load_scores_from_json(output_dir)

    if len(all_scores) < 2:
        print("Need at least 2 model score files (scores_*.json) for RQ1 analysis.")
        print("Generate batch inputs first, run scoring, then place results here.")
        return

    # Compute pairwise agreement
    print("\n=== Computing Pairwise Agreement ===")
    agreement_results = compute_pairwise_agreement(all_scores)

    # Compute score distributions
    print("\n=== Computing Score Distributions ===")
    distributions = compute_score_distributions(all_scores)

    # Compute model comparison (Friedman + post-hoc)
    print("\n=== Computing Model Comparisons ===")
    model_names = sorted(all_scores.keys())
    common_adrs = sorted(
        set.intersection(*[set(all_scores[m].keys()) for m in model_names])
    )

    comparison_results = {}
    for dim_id in DIMENSION_ORDER:
        dim_scores = {}
        for model_name in model_names:
            dim_scores[model_name] = [
                all_scores[model_name][adr].get(dim_id, 2) for adr in common_adrs
            ]
        print(f"  Comparing models on {dim_id} {QUALITY_MODEL[dim_id].name}...")
        result = compare_models(dim_scores, dim_id)
        comparison_results[dim_id] = {
            "friedman_chi2": result.friedman_chi2,
            "friedman_p": result.friedman_p,
        }

    # Combine all results
    full_results = {
        "rq": "RQ1: Cross-Model Agreement",
        "n_models": len(model_names),
        "models": model_names,
        "n_adrs": len(common_adrs),
        "agreement": agreement_results,
        "distributions": distributions,
        "comparisons": comparison_results,
    }

    # Save results
    with open(output_path / "rq1_results.json", "w") as f:
        json.dump(full_results, f, indent=2)
    print(f"\nFull results saved to {output_path / 'rq1_results.json'}")

    # Generate paper tables
    generate_paper_tables(agreement_results, output_dir)

    # Print summary
    print("\n" + "=" * 60)
    print("RQ1 SUMMARY: Cross-Model Agreement")
    print("=" * 60)
    for dim_id in DIMENSION_ORDER:
        dim_data = agreement_results.get("per_dimension", {}).get(dim_id, {})
        alpha = dim_data.get("krippendorff_alpha", 0)
        print(f"  {dim_id} {QUALITY_MODEL[dim_id].name:30s} alpha={alpha:.3f}")

    print("\nPairwise QWK (overall):")
    for pair_key, metrics in agreement_results.get("overall", {}).items():
        print(f"  {pair_key}: QWK={metrics['qwk']:.3f}, rho={metrics['spearman_rho']:.3f}")


def _log(model_key: str, msg: str) -> None:
    """Print a log line with timestamp and model prefix."""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [{model_key}] {msg}", flush=True)


def run_online_scoring(
    adr_dir: str, output_dir: str, models: list[str] | None = None,
) -> None:
    """Score ADRs directly via API calls with rate limiting and checkpoint/resume.

    Designed for free-tier cloud APIs (Groq, Cerebras) that don't support batch.
    Saves progress after each ADR so multi-day runs can be interrupted safely.

    Produces both scores_<model>.json (median) and passes_<model>.json (per-pass).
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    adrs = parse_adr_directory(adr_dir)
    print(f"Parsed {len(adrs)} ADRs from {adr_dir}")

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
        scores_file = output_path / f"scores_{safe_name}.json"
        passes_file = output_path / f"passes_{safe_name}.json"

        # Load checkpoint if exists
        all_median_scores = {}
        all_pass_scores = {}
        if scores_file.exists():
            with open(scores_file) as f:
                all_median_scores = json.load(f)
        if passes_file.exists():
            with open(passes_file) as f:
                all_pass_scores = json.load(f)

        # Check API key
        api_key_env = config.get("api_key_env", "")
        if api_key_env and not os.environ.get(api_key_env):
            _log(model_key, f"ERROR: env var {api_key_env} not set — skipping")
            continue

        scorer = _create_scorer(config)
        rate_limit = config.get("rate_limit", {})
        rpm = rate_limit.get("rpm", 30)
        rpd = rate_limit.get("rpd")
        min_delay = 60.0 / rpm + 0.5  # seconds between requests, with safety margin

        requests_per_adr = len(DIMENSION_ORDER) * config["num_passes"]
        total_requests_today = 0
        scored = 0
        skipped = 0

        _log(model_key, f"START — {config['model_name']}, {rpm} RPM, "
             f"checkpoint: {len(all_median_scores)}/{len(adrs)} ADRs")

        for i, adr in enumerate(adrs):
            if adr.filename in all_median_scores:
                skipped += 1
                continue

            # Check daily request limit
            if rpd and (total_requests_today + requests_per_adr) > rpd:
                _log(model_key, f"Daily limit ({rpd} RPD) reached. Resume tomorrow.")
                break

            _log(model_key, f"ADR [{skipped + scored + 1}/{len(adrs)}] {adr.filename}")

            try:
                assessment = _score_adr_rate_limited(
                    scorer, model_key, adr.raw_content, adr.filename, min_delay,
                )
            except Exception as e:
                _log(model_key, f"ERROR: {e} — saving checkpoint and stopping.")
                break

            # Extract median and per-pass scores
            all_median_scores[adr.filename] = assessment.median_scores
            all_pass_scores[adr.filename] = {
                dim_id: [s.score for s in scores_list]
                for dim_id, scores_list in assessment.dimension_scores.items()
            }

            total_requests_today += requests_per_adr
            scored += 1

            # Save checkpoint after each ADR
            with open(scores_file, "w") as f:
                json.dump(all_median_scores, f, indent=2)
            with open(passes_file, "w") as f:
                json.dump(all_pass_scores, f, indent=2)

            remaining = len(adrs) - scored - skipped
            _log(model_key, f"  done — {scored} scored, {remaining} remaining")

        _log(model_key, f"FINISH — {scored} new, {len(all_median_scores)} total")


def _score_adr_rate_limited(
    scorer,
    model_key: str,
    adr_content: str,
    adr_filename: str,
    min_delay: float,
) -> ADRAssessment:
    """Score a single ADR with rate-limiting delay between API calls."""
    dims = DIMENSION_ORDER
    assessment = ADRAssessment(
        adr_filename=adr_filename,
        adr_content=adr_content,
        dimension_scores={d: [] for d in dims},
    )

    total_calls = scorer.num_passes * len(dims)
    call_num = 0

    for pass_num in range(1, scorer.num_passes + 1):
        for dim_id in dims:
            call_num += 1
            start = time.monotonic()
            score = None
            for attempt in range(4):  # up to 4 attempts (1 initial + 3 retries)
                try:
                    score = scorer.score_dimension(adr_content, dim_id, pass_num)
                    break
                except Exception as e:
                    err_str = str(e).lower()
                    # Daily token limits — don't retry, just raise immediately
                    if "tokens per day" in err_str or "token_quota_exceeded" in err_str:
                        raise
                    backoff = min_delay * (2 ** attempt) + 5
                    if attempt < 3:
                        _log(model_key, f"  RETRY {attempt+1}/3 {dim_id}/p{pass_num}: {e} (wait {backoff:.0f}s)")
                        time.sleep(backoff)
                    else:
                        raise

            assessment.dimension_scores[dim_id].append(score)

            elapsed = time.monotonic() - start
            remaining = min_delay - elapsed
            if remaining > 0:
                time.sleep(remaining)

            total_elapsed = time.monotonic() - start
            _log(model_key, f"  [{call_num}/{total_calls}] p{pass_num} {dim_id}={score.score} ({total_elapsed:.1f}s)")

    return assessment


def main():
    parser = argparse.ArgumentParser(description="RQ1: Cross-Model Agreement Experiment")
    parser.add_argument("--adr-dir", default="adrs/", help="ADR directory")
    parser.add_argument("--output-dir", default="data/results/rq1/", help="Output directory")
    parser.add_argument("--batch-input", action="store_true",
                        help="Generate batch input JSONL files")
    parser.add_argument("--batch-output", action="store_true",
                        help="Analyze batch output results")
    parser.add_argument("--online", action="store_true",
                        help="Score ADRs online via API (rate-limited, checkpoint/resume)")
    parser.add_argument("--models", nargs="*", default=None,
                        help="Specific model keys to process (default: all)")

    args = parser.parse_args()

    if args.batch_input:
        generate_batch_inputs(args.adr_dir, args.output_dir, args.models)
    elif args.online:
        run_online_scoring(args.adr_dir, args.output_dir, args.models)
    elif args.batch_output:
        analyze_results(args.output_dir)
    else:
        print("RQ1: Cross-Model Agreement Experiment\n")
        print("Available models:")
        for key, cfg in MODEL_CONFIGS.items():
            print(f"  {key:40s} ({cfg['class']})")
        print()
        print("Usage:")
        print("  Generate batch inputs:")
        print("    python scripts/run_rq1_cross_model.py --batch-input --models gemini-2.5-flash")
        print("  Score online (rate-limited, checkpoint/resume):")
        print("    python scripts/run_rq1_cross_model.py --online --models llama-4-scout")
        print("    python scripts/run_rq1_cross_model.py --online --models qwen3-32b")
        print("    python scripts/run_rq1_cross_model.py --online --models mistral-large")
        print("  Analyze all results:")
        print("    python scripts/run_rq1_cross_model.py --batch-output")


if __name__ == "__main__":
    main()
