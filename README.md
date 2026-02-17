# Automated ADR Quality Assessment with LLMs

Replication package for the paper **"Automated Quality Assessment of Architectural Decision Records Using Large Language Models"**, submitted to *Empirical Software Engineering* (EMSE).

This study validates LLM-based scoring of Architectural Decision Records (ADRs) **without human annotation**, using cross-model agreement, convergent validity, perturbation sensitivity, and robustness analysis.

## Key Results

| Research Question | Key Finding |
|---|---|
| **RQ1** Cross-Model Agreement | 4 LLMs achieve substantial agreement on B2 Alternatives Coverage (QWK 0.64-0.96) and B5 Decision Specificity (QWK 0.49-0.80); Krippendorff's alpha = 0.711 and 0.678 respectively |
| **RQ2** Convergent Validity | LLM scores correlate with objective structural features where expected (e.g., section presence -> completeness) and diverge where content judgment is required |
| **RQ3** Perturbation Sensitivity | All 4 models detect targeted degradations with large effect sizes (Cliff's delta > 0.5) for section removal perturbations |
| **RQ4** Robustness | Scores are stable across repeated runs (ICC(3,k) > 0.80 for most dimensions), prompt variants, and formatting differences |

## Corpus

109 student-written ADRs from 2 university cohorts:

| Cohort | Count | Format | Description |
|--------|-------|--------|-------------|
| 2024 | 66 | Markdown headings | Standard `.md` files |
| 2025 | 43 | Plain-text headings | Google Docs exports |

Mean word count: 330 +/- 147. Both cohorts have comparable content volume (Cliff's delta = -0.035, negligible) despite different formatting.

## Models

4 models from 4 independently trained families:

| Model | Developer | Architecture | API Provider |
|-------|-----------|-------------|--------------|
| Gemini 2.5 Flash | Google DeepMind | Proprietary MoE | Google Gemini API |
| Llama 4 Scout 17B | Meta | MoE (16 experts) | NVIDIA NIM |
| GPT-OSS 20B | OpenAI | Dense transformer | NVIDIA NIM |
| Nemotron Nano 30B | NVIDIA | Dense transformer | NVIDIA NIM |

Each ADR is scored 5 times per model across 10 quality dimensions (median aggregated), yielding 21,800 total assessments for RQ1.

## Quality Model

10 dimensions on a 4-point anchored Likert scale (no neutral midpoint):

| Category | ID | Dimension |
|----------|----|-----------|
| Structural | A1 | Completeness |
| | A2 | Structural Conformance |
| Content | B1 | Context Adequacy |
| | B2 | Alternatives Coverage |
| | B3 | Rationale Depth |
| | B4 | Consequence Specificity |
| | B5 | Decision Specificity |
| Documentation | C1 | Clarity and Readability |
| | C2 | Consistency |
| | C3 | Traceability |

## Repository Structure

```
adr-quality-assessment/
├── README.md                 # This file
├── pyproject.toml            # Python package configuration
├── .env.example              # API key template
├── LICENSE                   # MIT license
│
├── src/adr_analyser/         # Core Python package
│   ├── parsing/              #   ADR parser + section extractor
│   ├── scoring/              #   LLM scorers (Gemini, vLLM/NIM)
│   ├── quality_model/        #   10-dimension model + rubric
│   ├── aggregation/          #   Weighted composite scoring
│   ├── evaluation/           #   Agreement, IRR, comparison, stability
│   ├── perturbation/         #   Degradation generator (10 types)
│   ├── baselines/            #   Non-LLM baselines
│   └── feedback/             #   LLM feedback generation
│
├── scripts/                  # Experiment execution scripts
│   ├── run_rq1_cross_model.py
│   ├── run_rq2_convergent_validity.py
│   ├── run_rq3_perturbation.py
│   ├── run_rq4_robustness.py
│   ├── run_analysis.py
│   └── test_rq1_models.py    # API connectivity smoke test
│
├── tests/                    # Unit tests
│   ├── test_parsing.py
│   ├── test_quality_model.py
│   ├── test_scoring_vllm.py
│   ├── test_aggregation.py
│   ├── test_evaluation.py
│   └── test_perturbation.py
│
├── adrs/                     # ADR corpus (109 files)
│   ├── 2024/                 #   66 ADRs (markdown headings)
│   └── 2025/                 #   43 ADRs (plain-text headings)
│
├── instruments/              # Quality model documentation
│   ├── annotation_codebook.md
│   └── survey_instrument.md
│
└── data/results/             # Pre-computed experiment results
    ├── corpus_analysis.json
    ├── paper_tables.md
    ├── rq1/                  # Cross-model agreement
    ├── rq2/                  # Convergent validity (MTMM)
    ├── rq3/                  # Perturbation sensitivity
    └── rq4/                  # Robustness analysis
```

## Setup

### Prerequisites

- Python >= 3.10
- API keys for Google Gemini and NVIDIA NIM

### Installation

```bash
git clone https://github.com/<your-org>/adr-quality-assessment.git
cd adr-quality-assessment

python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows

pip install -e ".[dev]"
```

### API Keys

Copy the template and add your API keys:

```bash
cp .env.example .env
# Edit .env with your keys
```

You need:
- `GOOGLE_API_KEY` - Google Gemini API key (for Gemini 2.5 Flash)
- `NVIDIA_API_KEY` - NVIDIA NIM API key (for Llama 4 Scout, GPT-OSS 20B, Nemotron Nano 30B)

### Verify Installation

```bash
# Run unit tests
pytest tests/ -v

# Verify API connectivity (requires API keys)
python scripts/test_rq1_models.py
```

## Reproducing Results

All experiment results are pre-computed in `data/results/`. To re-run from scratch:

### RQ1: Cross-Model Agreement

Score all 109 ADRs with 4 models (5 passes each, 10 dimensions):

```bash
# Run one model at a time (checkpoint/resume built in)
python scripts/run_rq1_cross_model.py --online --models gemini-2.5-flash --adr-dir adrs/ --output-dir data/results/rq1/
python scripts/run_rq1_cross_model.py --online --models llama-4-scout --adr-dir adrs/ --output-dir data/results/rq1/
python scripts/run_rq1_cross_model.py --online --models gpt-oss-20b --adr-dir adrs/ --output-dir data/results/rq1/
python scripts/run_rq1_cross_model.py --online --models nemotron-nano --adr-dir adrs/ --output-dir data/results/rq1/

# Analyze (after all models complete)
python scripts/run_rq1_cross_model.py --batch-output --output-dir data/results/rq1/
```

**Output**: `data/results/rq1/rq1_results.json` (pairwise QWK, ICC, Spearman, Krippendorff's alpha)

### RQ2: Convergent Validity

Correlate LLM quality scores with 20 objective structural/textual features:

```bash
python scripts/run_rq2_convergent_validity.py --scores-dir data/results/rq1/
```

**Output**: `data/results/rq2/rq2_mtmm_<model>.json` (MTMM correlations per model)

### RQ3: Perturbation Sensitivity

Apply 10 degradation types to 93 candidate ADRs and measure LLM detection:

```bash
# Generate perturbations
python scripts/run_rq3_perturbation.py --generate --adr-dir adrs/

# Score perturbations and analyze
python scripts/run_rq3_perturbation.py --analyze --output-dir data/results/rq3/
```

**Output**: `data/results/rq3/rq3_results.json` (detection rates, effect sizes per perturbation type)

### RQ4: Robustness

Test stability, prompt variants, and cross-format generalization:

```bash
python scripts/run_rq4_robustness.py --all --adr-dir adrs/ --scores-dir data/results/rq1/ --output-dir data/results/rq4/
```

**Output**: `data/results/rq4/rq4a_stability.json`, `rq4b_prompt_sensitivity.json`, `rq4c_cross_format.json`

## Pre-Computed Results

### RQ1 Output Files

| File | Description |
|------|-------------|
| `scores_<model>.json` | Median scores per ADR per dimension |
| `passes_<model>.json` | All 5 per-pass scores per ADR per dimension |
| `rq1_results.json` | Full pairwise agreement analysis (QWK, ICC, Spearman, Krippendorff's alpha) |
| `rq1_agreement_table.md` | Paper-ready agreement table |

### RQ2 Output Files

| File | Description |
|------|-------------|
| `objective_features.json` | 20 structural/textual features for all 109 ADRs |
| `rq2_mtmm_<model>.json` | MTMM correlation matrix per model |
| `rq2_mtmm_section_baseline.json` | Non-LLM section-count baseline |
| `rq2_mtmm_word_baseline.json` | Non-LLM word-count baseline |

### RQ3 Output Files

| File | Description |
|------|-------------|
| `perturbation_manifest.json` | Metadata for all 851 perturbations |
| `perturbation_scores_<model>.json` | LLM scores for perturbed ADRs |
| `rq3_results.json` | Detection rates and effect sizes |

### RQ4 Output Files

| File | Description |
|------|-------------|
| `rq4a_stability.json` | ICC(3,k) test-retest reliability per model/dimension |
| `rq4b_prompt_sensitivity.json` | Score differences across 3 prompt variants |
| `rq4c_cross_format.json` | Score differences between markdown and plain-text ADRs |
| `scores_<variant>_<model>.json` | Raw scores for each prompt variant |

## Architecture

### Scoring Pipeline

1. **Parsing** (`parsing/parser.py`): ADR files -> `ParsedADR` dataclass (raw content, body, metadata, headings)
2. **Section extraction** (`parsing/section_extractor.py`): `ParsedADR` -> `ExtractedSections` with plain-text fallback for 2025 cohort
3. **Prompt construction** (`scoring/prompts.py`): G-Eval framework -- one LLM call per dimension with chain-of-thought + few-shot examples
4. **Scoring** (`scoring/gemini_scorer.py` or `scoring/vllm_scorer.py`): 5 inference passes -> median score per dimension
5. **Aggregation** (`aggregation/aggregator.py`): Weighted composite scores -> quality tiers

### Scorer Implementations

- **GeminiScorer**: Google Gemini API with structured JSON output via `response_schema`
- **VLLMScorer**: OpenAI-compatible client for NVIDIA NIM endpoints. Includes `<think>` tag stripping and JSON recovery for reasoning models.

### Evaluation Modules

- `evaluation/agreement.py`: Pairwise metrics (QWK, ICC(2,1), Spearman, MAE, exact/adjacent agreement, Bland-Altman)
- `evaluation/irr.py`: Multi-rater Krippendorff's alpha (ordinal)
- `evaluation/comparison.py`: Friedman test + Cliff's delta for model comparison
- `evaluation/stability.py`: ICC(3,k) for test-retest reliability

## Development

```bash
# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/ scripts/

# Format
ruff format src/ tests/ scripts/
```



## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
