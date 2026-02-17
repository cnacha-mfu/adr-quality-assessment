#!/usr/bin/env python3
"""Smoke test: verify each RQ1 model can score one ADR dimension successfully."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Load .env
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value

from adr_analyser.parsing.parser import parse_adr_directory
from adr_analyser.scoring.gemini_scorer import GeminiScorer
from adr_analyser.scoring.vllm_scorer import VLLMScorer

MODEL_CONFIGS = {
    "gemini-2.5-flash": {
        "class": "GeminiScorer",
        "model_name": "gemini-2.5-flash",
        "temperature": 0.0,
        "num_passes": 1,
        "api_key_env": "GOOGLE_API_KEY",
    },
    "llama-4-scout": {
        "class": "VLLMScorer",
        "model_name": "meta/llama-4-scout-17b-16e-instruct",
        "api_base": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY",
        "temperature": 0.0,
        "num_passes": 1,
        "max_tokens": 2048,
    },
    "qwq-32b": {
        "class": "VLLMScorer",
        "model_name": "qwen/qwq-32b",
        "api_base": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY_2",
        "temperature": 0.0,
        "num_passes": 1,
        "max_tokens": 2048,
    },
    "gpt-oss-20b": {
        "class": "VLLMScorer",
        "model_name": "openai/gpt-oss-20b",
        "api_base": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY_3",
        "temperature": 0.0,
        "num_passes": 1,
        "max_tokens": 2048,
    },
    "mistral-large": {
        "class": "VLLMScorer",
        "model_name": "mistral-large-latest",
        "api_base": "https://api.mistral.ai/v1",
        "api_key_env": "MISTRAL_API_KEY",
        "temperature": 0.0,
        "num_passes": 1,
        "max_tokens": 2048,
    },
}

TEST_DIM = "A1"  # Test with one dimension: Completeness


def create_scorer(config):
    if config["class"] == "GeminiScorer":
        return GeminiScorer(
            model_name=config["model_name"],
            temperature=config["temperature"],
            num_passes=config["num_passes"],
        )
    else:
        api_key = os.environ.get(config["api_key_env"], "EMPTY")
        return VLLMScorer(
            model_name=config["model_name"],
            api_base=config["api_base"],
            api_key=api_key,
            temperature=config["temperature"],
            num_passes=config["num_passes"],
            max_tokens=config.get("max_tokens", 2048),
        )


def main():
    # Parse one ADR for testing
    adrs = parse_adr_directory("adrs/")
    if not adrs:
        print("FAIL: No ADRs found in adrs/")
        sys.exit(1)

    test_adr = adrs[0]
    print(f"Test ADR: {test_adr.filename}")
    print(f"Test dimension: {TEST_DIM}")
    print(f"{'=' * 60}\n")

    results = {}
    for model_key, config in MODEL_CONFIGS.items():
        # Check API key
        api_key_env = config.get("api_key_env", "")
        if api_key_env and not os.environ.get(api_key_env):
            print(f"[{model_key}] SKIP - {api_key_env} not set")
            results[model_key] = "SKIP"
            continue

        print(f"[{model_key}] Testing...", end=" ", flush=True)
        try:
            scorer = create_scorer(config)
            start = time.monotonic()
            score = scorer.score_dimension(test_adr.raw_content, TEST_DIM, pass_number=1)
            elapsed = time.monotonic() - start
            print(f"OK  (score={score.score}, {elapsed:.1f}s)")
            results[model_key] = "OK"
        except Exception as e:
            print(f"FAIL  ({e})")
            results[model_key] = f"FAIL: {e}"

        # Small delay between models to avoid rate issues
        time.sleep(2)

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    all_ok = True
    for model_key, status in results.items():
        marker = "+" if status == "OK" else ("-" if status == "SKIP" else "X")
        print(f"  [{marker}] {model_key}: {status}")
        if status.startswith("FAIL"):
            all_ok = False

    if all_ok:
        print("\nAll models passed. Safe to run the full experiment.")
    else:
        print("\nSome models failed. Fix issues before running the full experiment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
