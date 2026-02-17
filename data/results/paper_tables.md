# Paper-Ready Results — ADR Quality Assessment Study

Generated from analysis of 109 student-written ADRs (2024–2025 cohorts).

---

## Table 1: Dataset Characterization

| Metric | Overall (N=109) | 2024 (N=66) | 2025 (N=43) |
|--------|:---------:|:---------:|:---------:|
| Word count (mean ± SD) | 330 ± 147 | 331 ± 162 | 327 ± 123 |
| Word count (median) | 299 | 294 | 311 |
| Word count (Q1–Q3) | 237–387 | — | — |
| Word count (min–max) | 118–1,232 | — | — |
| Heading count (mean ± SD) | 4.0 ± 3.4 | 6.2 ± 2.1 | 0.7 ± 2.5 |
| Has code block (%) | 10.1% | 16.7% | 0.0% |
| Has metadata (%) | 0.0% | 0.0% | 0.0% |
| Uses markdown headings (%) | 60.6% | 100% | 0.0% |

**Key finding**: The two cohorts have comparable word counts (U=1369, p=.759, δ=−0.035, negligible) but dramatically different formatting: 2024 ADRs use standard markdown headings while 2025 ADRs use plain-text headings (likely from Google Docs export). This formatting difference (δ=0.880, large effect) is a confound that the assessment pipeline must handle robustly.

---

## Table 2: Section Presence Analysis

| Section | Overall (%) | 2024 (%) | 2025 (%) |
|---------|:---------:|:-------:|:-------:|
| Context / Problem Statement | 83.5% | 92.4% | 69.8% |
| Decision | 84.4% | 89.4% | 76.7% |
| Rationale / Justification | 84.4% | 90.9% | 74.4% |
| Consequences | 53.2% | 75.8% | 18.6% |
| Pros (explicit subsection) | 35.8% | 16.7% | 65.1% |
| Cons (explicit subsection) | 33.9% | 16.7% | 60.5% |
| Decision Outcome | 0.0% | 0.0% | 0.0% |
| Decision Drivers | 0.0% | 0.0% | 0.0% |
| Considered Options | 0.0% | 0.0% | 0.0% |
| Confirmation | 0.0% | 0.0% | 0.0% |
| More Information / Links | 0.0% | 0.0% | 0.0% |
| Sample Code | 73.4% | 81.8% | 60.5% |

| Summary Metric | Mean ± SD |
|----------------|:---------:|
| Mandatory sections present | 2.52 ± 0.72 |
| Optional sections present | 0.84 ± 0.78 |
| Total sections present | 3.37 ± 1.06 |

**Key findings**:
1. The three core MADR sections (Context, Decision, Rationale) are present in ~84% of ADRs — this is the structural backbone that students consistently include.
2. No ADR uses advanced MADR sections (Decision Drivers, Considered Options, Confirmation, Links) — a clear quality gap and opportunity for the feedback system.
3. The 2025 cohort uses explicit Pros/Cons subsections more frequently (65%/61% vs 17%/17%), while the 2024 cohort embeds them within a broader Consequences section (76% vs 19%).
4. 73% of ADRs include sample code, though this is supplementary material and should not influence quality scores.

---

## Table 3: Non-LLM Baseline Predictions

### 3a: Per-Dimension Baseline Scores (Mean ± SD)

| Dimension | Section-Count BL | Word-Count BL |
|-----------|:---------------:|:-------------:|
| A1 Completeness | 2.61 ± 0.72 | 3.20 ± 0.47 |
| A2 Structural Conformance | 2.06 ± 0.98 | 3.20 ± 0.47 |
| B1 Context Adequacy | 1.75 ± 0.43 | 3.20 ± 0.47 |
| B2 Alternatives Coverage | 1.75 ± 0.43 | 3.20 ± 0.47 |
| B3 Rationale Depth | 1.75 ± 0.43 | 3.20 ± 0.47 |
| B4 Consequence Specificity | 1.75 ± 0.43 | 3.20 ± 0.47 |
| B5 Decision Specificity | 1.75 ± 0.43 | 3.20 ± 0.47 |
| C1 Clarity and Readability | 1.75 ± 0.43 | 3.20 ± 0.47 |
| C2 Consistency | 1.75 ± 0.43 | 3.20 ± 0.47 |
| C3 Traceability | 1.75 ± 0.43 | 3.20 ± 0.47 |
| **Overall composite** | **1.87 ± 0.47** | **3.20 ± 0.47** |

### 3b: Quality Tier Distribution

| Quality Tier | Section-Count BL | Word-Count BL |
|-------------|:----------------:|:-------------:|
| Excellent (≥3.5) | 0 (0.0%) | 25 (22.9%) |
| Good (2.5–3.49) | 0 (0.0%) | 81 (74.3%) |
| Needs Improvement (1.5–2.49) | 82 (75.2%) | 3 (2.8%) |
| Poor (<1.5) | 27 (24.8%) | 0 (0.0%) |

**Key findings**:
1. The two baselines produce dramatically different predictions: section-count assigns 100% of ADRs to "Needs Improvement" or "Poor", while word-count assigns 97% to "Good" or "Excellent".
2. Word-count baseline produces identical scores across all dimensions (by design), demonstrating it cannot differentiate quality aspects — it is a pure length proxy.
3. Section-count baseline differentiates between structural dimensions (A1, A2) and content/documentation dimensions but assigns uniform scores within those groups.
4. Neither baseline captures content quality (B1–B5) or documentation quality (C1–C3) — this is the gap that LLM-based assessment addresses.
5. Correlation between baselines is negligible (ρ=−0.126, p=.192), confirming they measure different surface features.
6. Word count is uncorrelated with section count (ρ=−0.096, p=.319), indicating these are independent structural features.

---

## Table 4: Cross-Cohort Comparison

| Metric | 2024 (N=66) | 2025 (N=43) | U | p | Cliff's δ | Interpretation |
|--------|:-----------:|:-----------:|:---:|:---:|:---------:|:---------:|
| Word count | 331 ± 162 | 327 ± 123 | 1369 | .759 | −0.035 | Negligible |
| Heading count | 6.2 ± 2.1 | 0.7 ± 2.5 | 2669 | <.001 | 0.880 | Large |
| Section count | 3.6 ± 0.8 | 3.0 ± 1.2 | 1763 | .005 | 0.242 | Small |

### Baseline Scores by Cohort (Section-Count BL)

| Dimension | 2024 Mean | 2025 Mean | U | p | δ |
|-----------|:---------:|:---------:|:---:|:---:|:---:|
| A1 Completeness | 2.77 | 2.37 | 1772 | .004* | 0.249 (small) |
| A2 Structural Conformance | 2.74 | 1.00 | 2709 | <.001* | 0.909 (large) |
| B1–B5 Content dimensions | 1.85 | 1.60 | 1765 | .004* | 0.244 (small) |
| C1–C3 Documentation dims | 1.85 | 1.60 | 1765 | .004* | 0.244 (small) |

**Key findings**:
1. No significant difference in word count between cohorts — both produce similarly-sized documents.
2. The large effect on heading count (δ=0.880) reflects a formatting difference (markdown vs. plain text), not a content quality difference.
3. After adjusting for formatting, the section-count difference is small (δ=0.242), suggesting comparable structural quality.
4. A2 (Structural Conformance) shows the largest cohort difference (δ=0.909) — this is entirely attributable to the formatting difference and should be interpreted cautiously.

---

## Table 5: Correlation Analysis

| Variable Pair | Spearman ρ | p-value | Interpretation |
|---------------|:----------:|:-------:|:---------:|
| Word count ↔ Section count | −0.096 | .319 | Not significant |
| Section BL ↔ Word BL composites | −0.126 | .192 | Not significant |
| Word count ↔ Section BL composite | −0.133 | .168 | Not significant |
| Word count ↔ Word BL composite | 0.760 | <.001 | Strong positive |

**Key finding**: The strong correlation between word count and the word-count baseline (ρ=0.760) is trivially expected (by construction). The absence of correlation between word count and section-count baseline (ρ=−0.133, ns) confirms these baselines capture orthogonal surface features, neither of which alone predicts content quality.

---

## Table 6: Quality Gap Analysis (Absent MADR Sections)

| MADR Section | Present (%) | Quality Implication |
|-------------|:----------:|---------------------|
| Decision Drivers | 0.0% | Students do not explicitly identify the forces motivating their decisions |
| Considered Options | 0.0% | No systematic comparison of alternatives (Zimmermann requires ≥2) |
| Decision Outcome | 0.0% | No explicit "Chosen option: X, because Y" statement |
| Confirmation | 0.0% | No validation criteria for the decision |
| Links / References | 0.0% | No traceability to external artifacts |

This table documents the "quality ceiling" of the student ADR corpus: even the best-written ADRs in the dataset omit entire quality dimensions that MADR recommends. This gap is precisely what the LLM feedback system can address by providing actionable improvement suggestions.

---

## Summary Statistics for Paper

- **Corpus**: 109 student-written ADRs from 2 cohorts (66 from 2024, 43 from 2025)
- **Format diversity**: Two distinct formatting styles (markdown headings vs. plain text) requiring robust parsing
- **Core sections present**: Context (83.5%), Decision (84.4%), Rationale (84.4%)
- **Advanced sections absent**: Decision Drivers (0%), Considered Options (0%), Links (0%)
- **Non-LLM baselines demonstrate**: Surface features (word count, section count) cannot differentiate content quality dimensions
- **Cross-cohort stability**: Comparable content volume (δ=−0.035, ns) despite formatting differences (δ=0.880)
- **Quality gap**: 0% of ADRs include Considered Options — the most impactful improvement target

---

## Implications for the Assessment Pipeline

1. **Parser robustness**: The pipeline must handle both markdown and plain-text heading formats (implemented in `section_extractor.py`).
2. **Baseline inadequacy**: Non-LLM baselines produce either uniformly low (section-count) or uniformly high (word-count) predictions. They cannot discriminate between quality dimensions — validating the need for LLM-based assessment.
3. **Cohort fairness**: The A2 (Structural Conformance) dimension is confounded by formatting differences. LLM scorers should evaluate structural quality based on logical organization, not markdown syntax.
4. **Feedback focus**: The zero-presence of Considered Options, Decision Drivers, and Links sections identifies the highest-impact improvement targets for the feedback system.
