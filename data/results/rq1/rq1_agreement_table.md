# RQ1: Cross-Model Agreement Results

## Pairwise Agreement (QWK) Per Dimension

| Dimension | gemini-2.5-flash_vs_gpt-oss-20b | gemini-2.5-flash_vs_llama-4-scout | gemini-2.5-flash_vs_nemotron-nano-30b | gpt-oss-20b_vs_llama-4-scout | gpt-oss-20b_vs_nemotron-nano-30b | llama-4-scout_vs_nemotron-nano-30b | Kripp. alpha |
|-----------|:---------:|:---------:|:---------:|:---------:|:---------:|:---------:|:-----------:|
| A1 Completeness | 0.083 | 0.214 | 0.008 | 0.022 | -0.059 | -0.000 | -0.151 |
| A2 Structural Conformance | 0.241 | 0.066 | 0.474 | 0.045 | 0.282 | 0.114 | 0.064 |
| B1 Context Adequacy | 0.301 | 0.489 | 0.478 | 0.218 | 0.254 | 0.559 | 0.339 |
| B2 Alternatives Coverage | 0.641 | 0.524 | 0.619 | 0.751 | 0.964 | 0.784 | 0.711 |
| B3 Rationale Depth | 0.060 | 0.340 | 0.356 | -0.007 | 0.161 | 0.152 | 0.026 |
| B4 Consequence Specificity | 0.338 | 0.163 | 0.432 | 0.043 | 0.412 | 0.103 | 0.189 |
| B5 Decision Specificity | 0.801 | 0.493 | 0.783 | 0.488 | 0.771 | 0.672 | 0.678 |
| C1 Clarity and Readability | 0.516 | 0.174 | 0.516 | 0.095 | 0.451 | 0.170 | 0.366 |
| C2 Consistency | 0.502 | 0.427 | 0.279 | 0.257 | 0.364 | 0.368 | 0.360 |
| C3 Traceability | 0.214 | 0.135 | 0.405 | 0.026 | 0.491 | 0.042 | 0.121 |
| **Overall** | **0.023** | **0.385** | **0.253** | **0.008** | **0.128** | **0.087** | — |

## Interpretation Benchmarks
| QWK Range | Interpretation |
|-----------|---------------|
| 0.81-1.00 | Almost perfect |
| 0.61-0.80 | Substantial |
| 0.41-0.60 | Moderate |
| 0.21-0.40 | Fair |
| 0.00-0.20 | Slight |