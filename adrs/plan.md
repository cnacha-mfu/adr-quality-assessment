\# Automated ADR quality assessment with LLMs: a complete research plan for EMSE



\*\*This plan provides a phase-by-phase roadmap for building, validating, and publishing a study on LLM-based Architectural Decision Record quality assessment, targeting the Empirical Software Engineering journal.\*\* The study's novelty is threefold: no prior work automates ADR quality assessment, no validated ADR quality model exists, and the educational feedback loop creates direct practical impact. The plan synthesizes established methods from adjacent domains — automated essay scoring, requirements quality, LLM-as-a-Judge evaluation — and adapts them to the ADR context. One critical timing note: the EMSE special issue "Advancing Software Engineering with Large Language Models" (2025-SE-LLMs) had a deadline of \*\*November 28, 2025\*\*, which has passed. The researcher should contact the guest editors about late acceptance or plan to submit as a regular EMSE paper.



---



\## Phase 1: Constructing the ADR quality model (weeks 1–8)



No validated quality model for ADRs exists, so building one from scratch is the study's foundational contribution. The approach combines three established methods: \*\*literature-driven dimension extraction\*\*, \*\*expert validation via Delphi\*\*, and \*\*operationalization via GQM (Goal-Question-Metric)\*\*. This mirrors the process described by Siebert et al. (2022) in their quality model construction for ML systems, published in Software Quality Journal.



\*\*Step 1.1 — Extract candidate dimensions from literature and templates (weeks 1–3).\*\* Begin with the MADR 4.0.0 template structure, which defines mandatory sections (Context and Problem Statement, Considered Options, Decision Outcome) and optional sections (Decision Drivers, Pros/Cons, Consequences, Confirmation, More Information). Each section implies completeness criteria. Cross-reference with Zimmermann's 2023 "ADR Author Pledge" — seven principles including "present explicitly," "invest in documentation quality," and "be honest and candid" — plus his 11 anti-patterns. Layer in quality attributes from ISO/IEC/IEEE 42010:2022 (architecture description quality), IEEE 830 requirements quality characteristics (complete, consistent, unambiguous, traceable, verifiable), and the design rationale literature (QOC framework by MacLean et al., IBIS by Kunz \& Rittel). The proposed \*\*10-dimension hierarchical model\*\* organized into three categories is:



\*\*Structural quality:\*\* (A1) Completeness — all relevant MADR sections filled with substantive content; (A2) Structural conformance — adherence to template format, correct headings, metadata presence.



\*\*Content quality:\*\* (B1) Context adequacy — clarity of the problem, architectural significance, and decision drivers; (B2) Alternatives coverage — number, diversity, and feasibility of options considered (Zimmermann requires ≥2); (B3) Rationale depth — quality of justification with explicit because-clauses, reference to drivers, and tradeoff acknowledgment; (B4) Consequence specificity — concrete articulation of both positive and negative consequences; (B5) Decision specificity — how concrete, actionable, and unambiguous the chosen option is.



\*\*Documentation quality:\*\* (C1) Clarity and readability — language quality, logical flow, editorial polish; (C2) Consistency — no internal contradictions, uniform terminology, alignment between stated drivers and evaluation criteria; (C3) Traceability — explicit links to requirements, related ADRs, and external references.



\*\*Step 1.2 — Validate via modified Delphi method (weeks 3–6).\*\* Recruit \*\*5–10 experts\*\* spanning SE educators who teach architecture courses, practicing software architects, and ADR researchers. Zimmermann himself, Uwe van Heesch, and Rafael Capilla are key names in the field. Run \*\*2–3 Delphi rounds\*\* via online questionnaire: Round 1 asks experts to rate each dimension's importance (1–5 Likert), suggest additions/removals, and refine definitions; Round 2 presents aggregated results with anonymized justifications and asks for convergence; Round 3 (if needed) resolves remaining disagreements. Target \*\*≥70% agreement\*\* on retained dimensions. This takes approximately 2–3 weeks per round with asynchronous response.



\*\*Step 1.3 — Operationalize with GQM and create the scoring rubric (weeks 6–8).\*\* For each validated dimension, apply Basili's GQM paradigm. Example for Rationale Depth: Goal = "Assess justification quality of the decision outcome"; Questions = "Is there an explicit because-clause? Does the rationale reference decision drivers? Are tradeoffs acknowledged?"; Metrics = 4-point anchored Likert scale where 1 = "No rationale provided or only assertion without reasoning," 2 = "Generic rationale without reference to project context," 3 = "Rationale references drivers and acknowledges tradeoffs," 4 = "Exemplary rationale with evidence, explicit tradeoff analysis, and links to drivers." Use a \*\*4-point scale\*\* (not 5) to force discrimination and avoid central tendency bias. Create \*\*2–3 fully worked anchor examples\*\* at each quality level for every dimension — this codebook is the heart of reproducibility.



---



\## Phase 2: Building the expert-annotated ground truth (weeks 6–14)



\*\*Step 2.1 — Design the annotation protocol (week 6–7, overlapping with Phase 1).\*\* Create a detailed codebook document structured as: purpose and scope, dimension definitions with examples, scale anchors at each point, boundary cases, annotation procedure (read full ADR first, rate each dimension independently, record confidence and notes). Use an \*\*analytic rubric\*\* — separate scores per dimension — rather than holistic scoring. This yields richer data and typically higher inter-rater reliability because annotators focus on one aspect at a time.



\*\*Step 2.2 — Select and prepare annotators (week 7–8).\*\* Recruit \*\*3 annotators\*\*: two primary raters (SE doctoral students or instructors with architecture expertise) and one senior researcher as adjudicator. The minimum for computing inter-rater reliability is 2, but 3 enables majority voting and tie-breaking. All annotators must have software architecture expertise; they need not be the course instructor.



\*\*Step 2.3 — Run iterative pilot calibration (weeks 8–10).\*\* Conduct \*\*2–3 pilot rounds\*\* of 15–20 ADRs each. After each round, compute preliminary Krippendorff's alpha (ordinal), hold a calibration meeting to discuss every disagreement, and revise the codebook. Target \*\*α ≥ 0.67\*\* after Round 2 and \*\*α ≥ 0.80\*\* by Round 3. If a particular dimension consistently produces low agreement, consider simplifying its scale or splitting/merging it. This iterative calibration is the most critical quality gate in the entire study.



\*\*Step 2.4 — Full annotation (weeks 10–14).\*\* From the 2–3 years of student ADRs (likely \*\*200–500 documents\*\*), annotate \*\*200–300 ADRs\*\* using stratified sampling across cohorts, assignment topics, and estimated quality levels. \*\*Double-annotate 100%\*\* of the core dataset (both raters annotate every ADR independently), with the adjudicator resolving disagreements through consensus discussion. For practical tooling, use a \*\*structured Google Sheets spreadsheet\*\* — one row per ADR, columns for each dimension's score plus notes columns. This is the most common and transparent approach for document-level rating tasks in SE empirical studies. Alternatively, Label Studio (Community Edition) provides a more structured interface with audit trails.



\*\*Step 2.5 — Compute and report final IRR statistics.\*\* Report \*\*Krippendorff's alpha (ordinal)\*\* as the primary metric, \*\*quadratic weighted Cohen's kappa\*\* for pairwise comparison, and \*\*ICC(2,1) for absolute agreement\*\* with 95% bootstrap confidence intervals (10,000 resamples). Use Sim \& Wright's guideline that ≥30 items are needed for stable kappa estimates, though the full 200+ dataset will yield robust estimates. Report per-dimension IRR to identify which quality aspects are hardest to rate — this itself is a finding worth discussing.



---



\## Phase 3: Building the Claude Code assessment pipeline (weeks 8–16)



\*\*Step 3.1 — Design the pipeline architecture (week 8–10).\*\* Implement a 5-stage pipeline:



\*\*Stage 1: Parsing.\*\* Glob all `\*.md` files, parse YAML front matter (status, date, deciders), extract markdown body. Use Python's `python-markdown` or `mistune` library. Validate basic MADR structure presence.



\*\*Stage 2: Section extraction.\*\* Map MADR sections using regex patterns against standard headings (Context and Problem Statement, Decision Drivers, Considered Options, Decision Outcome, Pros/Cons subsections, Consequences, Confirmation, More Information). Output a structured dictionary per ADR with section content.



\*\*Stage 3: Per-dimension scoring (LLM-as-Judge).\*\* This is the core evaluation stage. Following the G-Eval framework (Liu et al., EMNLP 2023) and criteria decomposition best practices, \*\*evaluate each quality dimension in a separate LLM call\*\*. Research consistently shows single-aspect evaluation is more reliable than holistic multi-criteria scoring. Each call includes: the full rubric for that dimension with anchored scale descriptors, 1–2 few-shot examples of scored ADRs at different quality levels, and a chain-of-thought instruction ("First analyze the ADR against each criterion, then assign a score"). Require \*\*structured JSON output\*\* with `score`, `reasoning`, and `evidence` fields.



\*\*Stage 4: Score aggregation.\*\* Compute weighted composite scores using dimension weights validated through the Delphi process. Also record min score (weakest dimension), standard deviation (consistency across dimensions), and a classification tier (Excellent ≥3.5, Good 2.5–3.49, Needs Improvement 1.5–2.49, Poor <1.5 on the 4-point scale).



\*\*Stage 5: Feedback generation.\*\* A final LLM call takes all dimension scores with reasoning as input and generates: a 2–3 sentence overall assessment, top 3 strengths, top 3 specific improvement suggestions with references to rubric criteria, and (optionally) a suggested revision for the weakest section.



\*\*Step 3.2 — Implement using Claude's Batch API (weeks 10–13).\*\* Use the \*\*Claude Message Batches API\*\*, which processes up to 10,000 requests per batch at \*\*50% cost reduction\*\*. Leverage prompt caching — the system prompt containing the rubric and few-shot examples remains identical across all ADRs, yielding \*\*30–98% cache hit rates\*\*. Use Claude's \*\*structured output mode\*\* (JSON schema constraint via `output\_config.format`) to guarantee valid JSON responses matching the scoring schema. Set `temperature=0` for maximum determinism. Run \*\*5 inference passes\*\* per ADR to quantify non-determinism; use the median score as the final assessment.



The concrete implementation approach: write a Python script that constructs batch requests, each with `custom\_id` set to the ADR filename, identical system prompt with rubric and examples, and user message containing the extracted ADR content. Submit via `client.messages.batches.create()`, poll for completion, then parse the `.jsonl` results file.



\*\*Step 3.3 — Implement open-source baselines (weeks 13–16).\*\* Include \*\*two open-source baselines\*\* for reproducibility — this directly addresses EMSE's top reviewer concern. \*\*Prometheus 2\*\* (Kim et al., ICLR 2024) is the primary open-source baseline: it is a purpose-built evaluation model achieving Pearson r = 0.897 with human evaluators, accepts custom scoring rubrics, and supports both direct assessment and pairwise ranking. The 7B variant requires only 16GB VRAM. \*\*Llama 3.3 70B\*\* serves as the second baseline, representing general-purpose open-source capability. Deploy both via \*\*vLLM\*\* for reproducible, high-throughput inference with an OpenAI-compatible API. Use identical prompts and scoring schemas across all three models to enable fair comparison.



\*\*Step 3.4 — Implement non-LLM baselines (week 14–15).\*\* Create simple baselines that reviewers will expect: (1) \*\*random scoring\*\* from the same distribution as human labels; (2) \*\*section-count heuristic\*\* — completeness proxy based on number of filled MADR sections; (3) \*\*word-count regression\*\* — linear model predicting quality from word count; (4) \*\*TF-IDF + Ridge Regression\*\* trained on expert-annotated data with cross-validation. These establish that the LLM adds genuine value beyond surface features.



---



\## Phase 4: Rigorous evaluation (weeks 14–20)



\*\*Step 4.1 — Define research questions.\*\* Structure around four RQs:



\*\*RQ1 (Agreement):\*\* To what extent do LLM-generated quality scores agree with expert annotations across quality dimensions? This is the core validation question.



\*\*RQ2 (Comparison):\*\* How does Claude's assessment accuracy compare to open-source models (Prometheus 2, Llama 3.3) and non-LLM baselines?



\*\*RQ3 (Robustness):\*\* How stable are LLM assessments across repeated runs, prompt variations, and student cohorts?



\*\*RQ4 (Educational value):\*\* How do students perceive and respond to LLM-generated quality feedback compared to instructor feedback?



\*\*Step 4.2 — Agreement analysis for RQ1 (weeks 14–16).\*\* Report the \*\*full metric suite\*\* for each quality dimension and overall: Spearman's ρ (primary rank correlation), quadratic weighted Cohen's kappa (QWK — the standard in automated essay scoring, where ASAP competition winners achieved ~0.81), ICC(2,1) for absolute agreement with 95% CI, mean absolute error and RMSE, exact agreement percentage and adjacent agreement percentage (within ±1), and \*\*Bland-Altman plots\*\* showing bias and limits of agreement. The critical benchmark: \*\*compare LLM-human agreement against human-human inter-annotator agreement\*\*. If the LLM-human kappa approaches the human-human kappa, the tool is validated as a viable assessor.



\*\*Step 4.3 — Comparative analysis for RQ2 (weeks 16–17).\*\* Use \*\*Friedman test\*\* (non-parametric repeated-measures) to compare all models on the same ADR set, followed by \*\*Nemenyi post-hoc tests\*\* or \*\*Wilcoxon signed-rank tests with Holm-Bonferroni correction\*\* for pairwise comparisons. Report \*\*Cliff's delta\*\* as the primary effect size — it is the preferred non-parametric effect size in EMSE because ADR quality scores are ordinal (thresholds: |δ| < 0.147 negligible, < 0.33 small, < 0.474 medium, ≥ 0.474 large). Always report effect sizes with \*\*95% bootstrap confidence intervals\*\*. Include an \*\*ablation study\*\* testing: full rubric vs. minimal instructions, 0-shot vs. 1-shot vs. 3-shot, with vs. without chain-of-thought, holistic vs. per-dimension scoring.



\*\*Step 4.4 — Stability analysis for RQ3 (weeks 17–18).\*\* With 5 runs per ADR already collected, compute: \*\*intra-LLM ICC(3,k)\*\* across runs (target > 0.90), mean within-ADR standard deviation, percentage of ADRs with identical scores across all runs, and maximum observed within-ADR range. Present these in a stability analysis table. Test \*\*cross-cohort generalizability\*\* using leave-one-cohort-out validation: develop prompts using ADRs from all cohorts except one, evaluate on the held-out cohort, and repeat for each cohort.



\*\*Step 4.5 — Prompt sensitivity analysis (week 18).\*\* Test 2–3 prompt variants per dimension (e.g., different rubric phrasings, different few-shot examples, varying levels of detail). If scores diverge by more than 1 point on the 4-point scale, flag that dimension as prompt-sensitive. Report the variance explained by prompt choice vs. true quality differences.



\*\*Step 4.6 — Statistical reporting standards.\*\* EMSE strongly expects \*\*effect sizes alongside p-values\*\*, consistent with the ASA statement on p-values (Wasserstein \& Lazar, 2016). Per Kampenes et al.'s 2007 systematic review, only 29% of SE experiments reported effect sizes — doing so rigorously is a differentiator. Report in APA style: "W = 234, p = .003, r = 0.42 \[95% CI: 0.21, 0.61], Cliff's δ = 0.38 \[0.15, 0.58]." Use BCa bootstrap with 10,000 resamples for all confidence intervals. Apply Holm-Bonferroni correction when making multiple comparisons across dimensions or models.



---



\## Phase 5: Educational feedback evaluation (weeks 16–28)



\*\*Step 5.1 — Obtain ethics approval (weeks 16–19, start ASAP).\*\* Submit an IRB/ethics application targeting \*\*exempt Category 1\*\* (research in established educational settings involving normal educational practices). Critical requirements: use a \*\*third party\*\* (colleague or TA) to administer consent — the instructor must not know who participated until after grades are assigned. Consent must state participation is voluntary and non-participation will not affect grades. If in the EU, GDPR applies: consider using locally hosted models (Llama via vLLM) to avoid cross-border data transfer to Anthropic's US-based servers, or obtain explicit consent for data transfer with Standard Contractual Clauses. For the \*\*retrospective dataset\*\* (existing 2–3 years of ADRs), submit a separate application for secondary analysis of de-identified data under exempt Category 4.



\*\*Step 5.2 — Design the experimental study (weeks 18–20).\*\* Given typical architecture class sizes of 30–80 students, use a \*\*within-subjects crossover design\*\* — each student receives both AI feedback and instructor feedback on different ADR assignments, with counterbalanced ordering. This eliminates between-subject variability and requires only ~34 students for medium effect size (d = 0.5) at α = 0.05 and power = 0.80. The primary outcome variable is \*\*ADR quality improvement\*\* measured by the validated rubric: normalized gain = (post\_score − pre\_score) / (max\_score − pre\_score). Secondary outcomes include revision behavior (do students revise more after AI feedback?), time-to-revision, and perceived feedback quality.



\*\*Step 5.3 — Develop the survey instrument (week 20–21).\*\* Compose a four-section instrument: \*\*Section A\*\* — demographics (5 items: program, year, prior ADR experience, AI tool familiarity, self-assessed architecture competence); \*\*Section B\*\* — adapted TAM items (12 items on 7-point Likert: 6 for Perceived Usefulness, 6 for Perceived Ease of Use, adapted to ADR feedback context); \*\*Section C\*\* — System Usability Scale (10 standard SUS items on 5-point Likert, scoring range 0–100, above 68 = above average); \*\*Section D\*\* — feedback quality perception (8–10 items covering helpfulness, accuracy, specificity, actionability, comprehensiveness, trustworthiness, and comparison to instructor feedback); \*\*Section E\*\* — open-ended questions (4–5 items on most/least helpful aspects, comparison with instructor feedback, and suggested improvements). Pilot with 5–10 students before deployment.



\*\*Step 5.4 — Run the study (weeks 22–28, one full semester or half-semester module).\*\* Weeks 1–2: pre-survey and baseline ADR submission. Weeks 3–10: intervention period with iterative ADR submissions, alternating feedback conditions per the crossover design. Weeks 11–12: final ADR submission and post-survey. Week 13: semi-structured interviews with 8–12 students (purposive sampling across quality levels and feedback conditions) to reach theoretical saturation. Collect interaction logs documenting which feedback items students actually addressed in revisions.



\*\*Step 5.5 — Analyze educational outcomes (weeks 26–28).\*\* Quantitative: paired Wilcoxon tests comparing quality improvement under AI vs. instructor feedback, with Cliff's delta for effect size. ANCOVA with pre-test scores as covariate if using between-subjects elements. SUS scoring (odd items: subtract 1; even items: subtract from 5; sum × 2.5). TAM analysis: compute Cronbach's alpha (target ≥ 0.7), report PU and PEU means with CIs. Qualitative: thematic coding of open-ended responses and interview transcripts using a deductive-inductive approach. Code for positive themes (helpfulness, specificity, timeliness), negative themes (hallucinations, generic feedback, over-reliance), and comparative themes (trust, preference, emotional response). Use two independent coders with IRR verification.



---



\## Phase 6: Paper writing and submission (weeks 24–32)



\*\*Step 6.1 — Structure the paper.\*\* Target \*\*35–45 pages\*\* in Springer SVJour3 LaTeX format. EMSE has no formal page limit but published empirical studies typically fall in this range. Use the SVJour3 template from Overleaf. Recommended structure:



\*\*Introduction\*\* (2–3 pages): Motivation (ADRs are increasingly adopted but quality varies widely, no automated assessment exists), research gap, and four contributions: (1) a validated ADR quality model, (2) an expert-annotated ADR dataset, (3) an LLM-based assessment pipeline with evaluation, (4) an educational feedback study.



\*\*Background and related work\*\* (4–5 pages): ADR documentation (Zimmermann's guidelines, MADR, Y-statement), documentation quality models (ISO 42010, requirements quality), LLM-as-Judge paradigm (Zheng et al. 2023, G-Eval), automated assessment in SE education (DAFeeD, Artemis platform).



\*\*ADR quality model\*\* (4–5 pages): Construction method (literature extraction → Delphi validation → GQM operationalization), the validated dimensions with rubric, and the Delphi results.



\*\*Ground truth dataset\*\* (3–4 pages): Annotation protocol, annotator training, IRR results per dimension, dataset statistics and distribution analysis.



\*\*Assessment pipeline\*\* (3–4 pages): Architecture diagram, prompt design with full prompts in appendix, Claude Batch API implementation, Prometheus 2 and Llama baselines, non-LLM baselines.



\*\*Evaluation\*\* (8–10 pages): Per-RQ results with full statistical reporting. Bland-Altman plots for agreement, comparison tables across models, stability analysis, ablation results.



\*\*Educational feedback study\*\* (5–6 pages): Experimental design, survey results (TAM, SUS, feedback quality), qualitative findings from interviews, learning gain analysis.



\*\*Discussion\*\* (3–4 pages): Implications for practice and education, comparison with automated essay scoring benchmarks, limitations of LLM-based evaluation.



\*\*Threats to validity\*\* (2–3 pages): Address construct (quality model captures "real" quality), internal (confounds in educational study), external (generalizability beyond MADR, beyond student ADRs), and conclusion (statistical power, non-determinism) validity. Explicitly address LLM-specific threats: data contamination, prompt sensitivity, model deprecation, closed-source reproducibility.



\*\*Step 6.2 — Address the top reviewer concerns proactively.\*\* Based on analysis of 85 LLM-centric papers at ICSE/ASE 2024, where \*\*none were fully reproducible\*\*, preemptively address: (1) \*\*Model specification\*\* — report exact model name and version (e.g., "claude-sonnet-4-5-20241022"), temperature (0), all sampling parameters; only 1/3 of LLM studies report temperature. (2) \*\*Reproducibility\*\* — include Prometheus 2 and Llama as open-source baselines that anyone can run. (3) \*\*Prompt sensitivity\*\* — include the ablation study. (4) \*\*Data contamination\*\* — student ADRs are private and cannot be in any training data; state this explicitly. (5) \*\*Cost transparency\*\* — report total API costs for all experiments. (6) Follow the \*\*8 community guidelines\*\* from Wagner et al. (2025, llm-guidelines.org): declare LLM usage, report configurations, document tool architecture, disclose all prompts, validate with humans, include open-source baseline, report suitable metrics, and articulate limitations.



\*\*Step 6.3 — Prepare the replication package.\*\* Host on \*\*Zenodo\*\* (not GitHub alone — Zenodo provides a DOI and archival guarantee). Include: anonymized ADR dataset with expert annotations, all prompts verbatim, Python scripts for the assessment pipeline, statistical analysis scripts (R or Python), survey instruments, and a detailed README. EMSE's Open Science Initiative awards a badge for reviewed replication packages, reviewed by a dedicated Open Science Board member post-acceptance.



\*\*Step 6.4 — Submit.\*\* Use Editorial Manager at editorialmanager.com/emse. For the special issue (if still accepting), select "Research Papers" → answer "Yes" to special issue → select "2025-SE-LLMs." Otherwise, submit as a regular paper. EMSE uses \*\*single-blind review\*\* with typically \*\*3 reviewers\*\*. Expect \*\*~12 weeks\*\* to first decision, with 6–12 months total to acceptance including revisions. Accepted papers publish immediately as Online First.



---



\## Phase 7: Realistic timeline summary



The total timeline from start to submission spans approximately \*\*8 months\*\* (32 weeks), with significant parallelism between phases:



| Phase | Activity | Weeks | Dependencies |

|-------|----------|-------|--------------|

| 1 | Quality model construction | 1–8 | None |

| 2 | Expert annotation | 6–14 | Rubric from Phase 1 |

| 3 | Pipeline implementation | 8–16 | Rubric from Phase 1 |

| 4 | Quantitative evaluation | 14–20 | Annotations + pipeline |

| 5a | Ethics approval | 16–19 | Study design |

| 5b | Educational study execution | 22–28 | Ethics approval + tool |

| 6 | Paper writing | 24–32 | All results |



\*\*Critical path\*\*: Quality model (8 weeks) → Annotation (8 weeks) → Evaluation (6 weeks) → Writing (8 weeks) = \*\*30 weeks minimum\*\*. The educational study runs partly in parallel but adds 6–10 weeks if not overlapping with a semester. If the researcher needs to wait for a new semester cohort, start Phases 1–4 immediately and plan Phase 5 for the next available semester. The paper can be structured to present the automated assessment as the primary contribution with the educational study as a secondary validation, allowing submission of Phases 1–4 results first with the educational component added in revision.



---



\## Essential references and tools at a glance



The most critical references to cite: Zimmermann (2023) on ADR creation and review guidelines; Kopp, Armbruster \& Zimmermann (2018) on MADR; Zheng et al. (2023) on LLM-as-Judge (NeurIPS); Liu et al. (2023) on G-Eval (EMNLP); Kim et al. (2024) on Prometheus 2 (ICLR); Basili \& Weiss (1984) on GQM; Siebert et al. (2022) on quality model construction; Davis (1989) on TAM; Kampenes et al. (2007) on effect sizes in SE; and the Wagner et al. (2025) community guidelines for LLM-based SE studies. Key tools: Claude Message Batches API with structured outputs for production assessment, vLLM for open-source model deployment, Prometheus 2 (7B) as the purpose-built evaluation baseline, Google Sheets or Label Studio for annotation, Zenodo for replication package hosting, and SVJour3 LaTeX template for formatting.



\## Conclusion



This plan transforms a straightforward classroom resource — years of student-written ADRs — into a novel research contribution addressing a genuine gap. The strongest strategic choice is \*\*separating the quality model construction as an independent contribution\*\* from the LLM automation, because the validated rubric has value regardless of the assessment technology. The educational feedback dimension grounds the work in real-world impact that EMSE reviewers value. The most likely failure modes to watch for are low inter-rater reliability on subjective dimensions like "rationale depth" (mitigate through iterative calibration) and LLM score inflation relative to human experts (mitigate through Bland-Altman analysis and explicit calibration). If the automated assessment achieves QWK > 0.60 with experts — comparable to early automated essay scoring systems — that alone is a publishable result for this entirely new domain.

