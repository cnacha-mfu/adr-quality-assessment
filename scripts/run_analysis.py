"""
Comprehensive analysis script for the ADR corpus.

Produces paper-ready results including:
1. Dataset characterization (Table 1 in paper)
2. Section presence/absence analysis (Table 2)
3. Non-LLM baseline predictions (Table 3)
4. Cross-cohort comparison (Table 4)
5. Distribution analysis and descriptive statistics
6. Quality dimension distribution from baselines
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats as scipy_stats

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from adr_analyser.aggregation.aggregator import aggregate_scores, QualityTier
from adr_analyser.baselines.non_llm import SectionCountBaseline, WordCountBaseline
from adr_analyser.parsing.parser import parse_adr_directory
from adr_analyser.parsing.section_extractor import extract_sections, ExtractedSections
from adr_analyser.quality_model.dimensions import (
    DIMENSION_ORDER,
    QUALITY_MODEL,
    QualityCategory,
)


def run_full_analysis(adr_dir: str = "/home/user/adr-analyser/adrs"):
    """Run all analyses and return results dict."""
    print("=" * 70)
    print("ADR CORPUS ANALYSIS — Paper-Ready Results")
    print("=" * 70)

    # ---------------------------------------------------------------
    # 1. Parse all ADRs
    # ---------------------------------------------------------------
    adrs = parse_adr_directory(adr_dir)
    print(f"\nTotal ADRs parsed: {len(adrs)}")

    # Extract sections for all ADRs
    adr_sections = []
    for adr in adrs:
        sections = extract_sections(adr)
        adr_sections.append((adr, sections))

    results = {}

    # ---------------------------------------------------------------
    # 2. TABLE 1: Dataset Characterization
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TABLE 1: Dataset Characterization")
    print("=" * 70)

    cohorts = {}
    for adr, sections in adr_sections:
        cohorts.setdefault(adr.cohort, []).append((adr, sections))

    word_counts = [adr.word_count for adr, _ in adr_sections]
    heading_counts = [adr.heading_count for adr, _ in adr_sections]

    table1 = {
        "total_adrs": len(adrs),
        "cohorts": {},
        "overall": {
            "word_count": {
                "mean": round(statistics.mean(word_counts), 1),
                "median": round(statistics.median(word_counts), 1),
                "std": round(statistics.stdev(word_counts), 1),
                "min": min(word_counts),
                "max": max(word_counts),
                "q1": round(np.percentile(word_counts, 25), 1),
                "q3": round(np.percentile(word_counts, 75), 1),
            },
            "heading_count": {
                "mean": round(statistics.mean(heading_counts), 1),
                "median": round(statistics.median(heading_counts), 1),
                "std": round(statistics.stdev(heading_counts), 1),
                "min": min(heading_counts),
                "max": max(heading_counts),
            },
            "has_code_block_pct": round(
                sum(1 for adr, _ in adr_sections if adr.has_code_block)
                / len(adrs) * 100, 1
            ),
            "has_metadata_pct": round(
                sum(1 for adr, _ in adr_sections if adr.metadata.status)
                / len(adrs) * 100, 1
            ),
        },
    }

    for cohort, items in sorted(cohorts.items()):
        wc = [adr.word_count for adr, _ in items]
        hc = [adr.heading_count for adr, _ in items]
        table1["cohorts"][cohort] = {
            "n": len(items),
            "word_count_mean": round(statistics.mean(wc), 1),
            "word_count_median": round(statistics.median(wc), 1),
            "word_count_std": round(statistics.stdev(wc), 1) if len(wc) > 1 else 0,
            "heading_count_mean": round(statistics.mean(hc), 1),
            "has_code_pct": round(
                sum(1 for adr, _ in items if adr.has_code_block) / len(items) * 100, 1
            ),
        }

    # Print Table 1
    print(f"\n{'Metric':<35} {'Overall':>10} ", end="")
    for c in sorted(cohorts.keys()):
        print(f"  {c:>10}", end="")
    print()
    print("-" * 70)

    print(f"{'Number of ADRs':<35} {table1['total_adrs']:>10} ", end="")
    for c in sorted(cohorts.keys()):
        print(f"  {table1['cohorts'][c]['n']:>10}", end="")
    print()

    wc = table1["overall"]["word_count"]
    print(f"{'Word count (mean ± std)':<35} {wc['mean']:>5.0f}±{wc['std']:<4.0f}", end="")
    for c in sorted(cohorts.keys()):
        cc = table1["cohorts"][c]
        print(f"  {cc['word_count_mean']:>5.0f}±{cc['word_count_std']:<4.0f}", end="")
    print()

    print(f"{'Word count (median)':<35} {wc['median']:>10.0f} ", end="")
    for c in sorted(cohorts.keys()):
        print(f"  {table1['cohorts'][c]['word_count_median']:>10.0f}", end="")
    print()

    print(f"{'Word count (min–max)':<35} {wc['min']:>4}–{wc['max']:<5}", end="")
    print()

    print(f"{'Word count (Q1–Q3)':<35} {wc['q1']:>4.0f}–{wc['q3']:<5.0f}")

    hc = table1["overall"]["heading_count"]
    print(f"{'Heading count (mean ± std)':<35} {hc['mean']:>5.1f}±{hc['std']:<4.1f}", end="")
    for c in sorted(cohorts.keys()):
        print(f"  {table1['cohorts'][c]['heading_count_mean']:>10.1f}", end="")
    print()

    print(f"{'Has code block (%)':<35} {table1['overall']['has_code_block_pct']:>9.1f}%", end="")
    for c in sorted(cohorts.keys()):
        print(f"  {table1['cohorts'][c]['has_code_pct']:>9.1f}%", end="")
    print()

    print(f"{'Has metadata (%)':<35} {table1['overall']['has_metadata_pct']:>9.1f}%")

    results["table1_dataset_characterization"] = table1

    # ---------------------------------------------------------------
    # 3. TABLE 2: Section Presence/Absence Analysis
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TABLE 2: Section Presence Analysis")
    print("=" * 70)

    section_fields = [
        ("context", "Context / Problem Statement"),
        ("decision", "Decision"),
        ("decision_outcome", "Decision Outcome"),
        ("decision_drivers", "Decision Drivers"),
        ("considered_options", "Considered Options"),
        ("rationale", "Rationale / Justification"),
        ("consequences", "Consequences"),
        ("pros", "Pros (explicit)"),
        ("cons", "Cons (explicit)"),
        ("confirmation", "Confirmation"),
        ("more_information", "More Information / Links"),
        ("issue", "Issue (non-standard)"),
        ("solution", "Solution (non-standard)"),
        ("sample_code", "Sample Code"),
    ]

    table2 = {}
    print(f"\n{'Section':<35} {'Overall':>8} {'%':>6}", end="")
    for c in sorted(cohorts.keys()):
        print(f"  {c+' %':>8}", end="")
    print()
    print("-" * 75)

    for field_name, display_name in section_fields:
        total_present = 0
        cohort_counts = {}

        for adr, sections in adr_sections:
            val = getattr(sections, field_name, None)
            present = val is not None and len(str(val).strip()) > 0
            if present:
                total_present += 1
                cohort_counts[adr.cohort] = cohort_counts.get(adr.cohort, 0) + 1

        pct = total_present / len(adrs) * 100
        table2[field_name] = {
            "total": total_present,
            "pct": round(pct, 1),
            "by_cohort": {},
        }

        print(f"{display_name:<35} {total_present:>5}/{len(adrs):<3} {pct:>5.1f}%", end="")
        for c in sorted(cohorts.keys()):
            n_cohort = len(cohorts[c])
            c_count = cohort_counts.get(c, 0)
            c_pct = c_count / n_cohort * 100 if n_cohort > 0 else 0
            table2[field_name]["by_cohort"][c] = {
                "count": c_count,
                "pct": round(c_pct, 1),
            }
            print(f"  {c_pct:>7.1f}%", end="")
        print()

    # Mandatory sections coverage
    mandatory_counts = [s.mandatory_sections_present for _, s in adr_sections]
    optional_counts = [s.optional_sections_present for _, s in adr_sections]
    total_counts = [s.total_sections_present for _, s in adr_sections]

    print(f"\n{'Mandatory sections present (mean)':<35} {statistics.mean(mandatory_counts):>8.2f}")
    print(f"{'Optional sections present (mean)':<35} {statistics.mean(optional_counts):>8.2f}")
    print(f"{'Total sections present (mean)':<35} {statistics.mean(total_counts):>8.2f}")

    table2["summary"] = {
        "mandatory_mean": round(statistics.mean(mandatory_counts), 2),
        "mandatory_std": round(statistics.stdev(mandatory_counts), 2) if len(mandatory_counts) > 1 else 0,
        "optional_mean": round(statistics.mean(optional_counts), 2),
        "optional_std": round(statistics.stdev(optional_counts), 2) if len(optional_counts) > 1 else 0,
        "total_mean": round(statistics.mean(total_counts), 2),
        "total_std": round(statistics.stdev(total_counts), 2) if len(total_counts) > 1 else 0,
    }

    results["table2_section_analysis"] = table2

    # ---------------------------------------------------------------
    # 4. TABLE 3: Non-LLM Baseline Results
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TABLE 3: Non-LLM Baseline Predictions")
    print("=" * 70)

    section_bl = SectionCountBaseline()
    word_bl = WordCountBaseline()

    section_results = []
    word_results = []
    all_section_scores = {d: [] for d in DIMENSION_ORDER}
    all_word_scores = {d: [] for d in DIMENSION_ORDER}

    for adr, sections in adr_sections:
        s_scores = section_bl.predict(adr)
        w_scores = word_bl.predict(adr)

        s_agg = aggregate_scores(adr.filename, s_scores)
        w_agg = aggregate_scores(adr.filename, w_scores)

        section_results.append(s_agg)
        word_results.append(w_agg)

        for d in DIMENSION_ORDER:
            all_section_scores[d].append(s_scores[d])
            all_word_scores[d].append(w_scores[d])

    # Per-dimension baseline averages
    print(f"\n{'Dimension':<25} {'Section BL':>12} {'Word BL':>12}")
    print(f"{'':25} {'Mean±Std':>12} {'Mean±Std':>12}")
    print("-" * 50)

    table3 = {"section_count": {}, "word_count": {}}

    for d in DIMENSION_ORDER:
        s_mean = statistics.mean(all_section_scores[d])
        s_std = statistics.stdev(all_section_scores[d]) if len(all_section_scores[d]) > 1 else 0
        w_mean = statistics.mean(all_word_scores[d])
        w_std = statistics.stdev(all_word_scores[d]) if len(all_word_scores[d]) > 1 else 0

        dim = QUALITY_MODEL[d]
        print(f"{d} {dim.name:<22} {s_mean:>5.2f}±{s_std:<5.2f} {w_mean:>5.2f}±{w_std:<5.2f}")

        table3["section_count"][d] = {
            "mean": round(s_mean, 2),
            "std": round(s_std, 2),
            "median": statistics.median(all_section_scores[d]),
        }
        table3["word_count"][d] = {
            "mean": round(w_mean, 2),
            "std": round(w_std, 2),
            "median": statistics.median(all_word_scores[d]),
        }

    # Overall composite
    s_composites = [r.weighted_composite for r in section_results]
    w_composites = [r.weighted_composite for r in word_results]

    print("-" * 50)
    print(
        f"{'Overall composite':<25} "
        f"{statistics.mean(s_composites):>5.2f}±{statistics.stdev(s_composites):<5.2f} "
        f"{statistics.mean(w_composites):>5.2f}±{statistics.stdev(w_composites):<5.2f}"
    )

    table3["section_count"]["overall"] = {
        "mean": round(statistics.mean(s_composites), 2),
        "std": round(statistics.stdev(s_composites), 2),
        "median": round(statistics.median(s_composites), 2),
    }
    table3["word_count"]["overall"] = {
        "mean": round(statistics.mean(w_composites), 2),
        "std": round(statistics.stdev(w_composites), 2),
        "median": round(statistics.median(w_composites), 2),
    }

    # Tier distribution
    print("\nQuality Tier Distribution:")
    print(f"{'Tier':<25} {'Section BL':>12} {'Word BL':>12}")
    print("-" * 50)

    for tier in QualityTier:
        s_count = sum(1 for r in section_results if r.tier == tier)
        w_count = sum(1 for r in word_results if r.tier == tier)
        s_pct = s_count / len(section_results) * 100
        w_pct = w_count / len(word_results) * 100
        print(f"{tier.value:<25} {s_count:>4} ({s_pct:>4.1f}%) {w_count:>4} ({w_pct:>4.1f}%)")

        table3.setdefault("tier_distribution", {})[tier.value] = {
            "section_count": s_count,
            "section_pct": round(s_pct, 1),
            "word_count": w_count,
            "word_pct": round(w_pct, 1),
        }

    results["table3_baseline_predictions"] = table3

    # ---------------------------------------------------------------
    # 5. TABLE 4: Cross-Cohort Comparison
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TABLE 4: Cross-Cohort Comparison (2024 vs 2025)")
    print("=" * 70)

    table4 = {}

    # Word count comparison
    wc_2024 = [adr.word_count for adr, _ in adr_sections if adr.cohort == "2024"]
    wc_2025 = [adr.word_count for adr, _ in adr_sections if adr.cohort == "2025"]

    u_stat, u_p = scipy_stats.mannwhitneyu(wc_2024, wc_2025, alternative="two-sided")

    # Cliff's delta for word count
    from adr_analyser.evaluation.comparison import compute_cliffs_delta
    cd_wc = compute_cliffs_delta(np.array(wc_2024), np.array(wc_2025), n_bootstrap=5000)

    print(f"\nWord count comparison:")
    print(f"  2024: mean={statistics.mean(wc_2024):.1f}, median={statistics.median(wc_2024):.0f}")
    print(f"  2025: mean={statistics.mean(wc_2025):.1f}, median={statistics.median(wc_2025):.0f}")
    print(f"  Mann-Whitney U={u_stat:.1f}, p={u_p:.4f}")
    print(f"  Cliff's delta={cd_wc.delta:.3f} ({cd_wc.interpretation}), "
          f"95% CI [{cd_wc.ci_lower:.3f}, {cd_wc.ci_upper:.3f}]")

    table4["word_count"] = {
        "2024_mean": round(statistics.mean(wc_2024), 1),
        "2024_median": round(statistics.median(wc_2024), 0),
        "2024_std": round(statistics.stdev(wc_2024), 1),
        "2025_mean": round(statistics.mean(wc_2025), 1),
        "2025_median": round(statistics.median(wc_2025), 0),
        "2025_std": round(statistics.stdev(wc_2025), 1),
        "mann_whitney_u": round(u_stat, 1),
        "p_value": round(u_p, 4),
        "cliffs_delta": cd_wc.delta,
        "cliffs_ci": [cd_wc.ci_lower, cd_wc.ci_upper],
        "cliffs_interpretation": cd_wc.interpretation,
    }

    # Heading count comparison
    hc_2024 = [adr.heading_count for adr, _ in adr_sections if adr.cohort == "2024"]
    hc_2025 = [adr.heading_count for adr, _ in adr_sections if adr.cohort == "2025"]

    u_stat_h, u_p_h = scipy_stats.mannwhitneyu(hc_2024, hc_2025, alternative="two-sided")
    cd_hc = compute_cliffs_delta(np.array(hc_2024), np.array(hc_2025), n_bootstrap=5000)

    print(f"\nHeading count comparison:")
    print(f"  2024: mean={statistics.mean(hc_2024):.1f}, median={statistics.median(hc_2024):.0f}")
    print(f"  2025: mean={statistics.mean(hc_2025):.1f}, median={statistics.median(hc_2025):.0f}")
    print(f"  Mann-Whitney U={u_stat_h:.1f}, p={u_p_h:.4f}")
    print(f"  Cliff's delta={cd_hc.delta:.3f} ({cd_hc.interpretation}), "
          f"95% CI [{cd_hc.ci_lower:.3f}, {cd_hc.ci_upper:.3f}]")

    table4["heading_count"] = {
        "2024_mean": round(statistics.mean(hc_2024), 1),
        "2025_mean": round(statistics.mean(hc_2025), 1),
        "mann_whitney_u": round(u_stat_h, 1),
        "p_value": round(u_p_h, 4),
        "cliffs_delta": cd_hc.delta,
        "cliffs_interpretation": cd_hc.interpretation,
    }

    # Section count comparison
    sc_2024 = [s.total_sections_present for adr, s in adr_sections if adr.cohort == "2024"]
    sc_2025 = [s.total_sections_present for adr, s in adr_sections if adr.cohort == "2025"]

    u_stat_s, u_p_s = scipy_stats.mannwhitneyu(sc_2024, sc_2025, alternative="two-sided")
    cd_sc = compute_cliffs_delta(np.array(sc_2024), np.array(sc_2025), n_bootstrap=5000)

    print(f"\nSection count comparison:")
    print(f"  2024: mean={statistics.mean(sc_2024):.1f}, median={statistics.median(sc_2024):.0f}")
    print(f"  2025: mean={statistics.mean(sc_2025):.1f}, median={statistics.median(sc_2025):.0f}")
    print(f"  Mann-Whitney U={u_stat_s:.1f}, p={u_p_s:.4f}")
    print(f"  Cliff's delta={cd_sc.delta:.3f} ({cd_sc.interpretation}), "
          f"95% CI [{cd_sc.ci_lower:.3f}, {cd_sc.ci_upper:.3f}]")

    table4["section_count"] = {
        "2024_mean": round(statistics.mean(sc_2024), 1),
        "2025_mean": round(statistics.mean(sc_2025), 1),
        "mann_whitney_u": round(u_stat_s, 1),
        "p_value": round(u_p_s, 4),
        "cliffs_delta": cd_sc.delta,
        "cliffs_interpretation": cd_sc.interpretation,
    }

    # Per-dimension baseline comparison by cohort
    print(f"\nSection-count baseline by cohort:")
    print(f"{'Dimension':<25} {'2024 Mean':>10} {'2025 Mean':>10} {'U':>8} {'p':>8} {'δ':>8}")
    print("-" * 72)

    table4["baseline_by_cohort"] = {}

    for d in DIMENSION_ORDER:
        scores_2024 = [
            section_bl.predict(adr)[d]
            for adr, _ in adr_sections if adr.cohort == "2024"
        ]
        scores_2025 = [
            section_bl.predict(adr)[d]
            for adr, _ in adr_sections if adr.cohort == "2025"
        ]

        try:
            u, p = scipy_stats.mannwhitneyu(scores_2024, scores_2025, alternative="two-sided")
        except ValueError:
            u, p = 0, 1.0

        cd = compute_cliffs_delta(
            np.array(scores_2024), np.array(scores_2025), n_bootstrap=2000
        )

        dim = QUALITY_MODEL[d]
        sig = "*" if p < 0.05 else ""
        print(
            f"{d} {dim.name:<22} {statistics.mean(scores_2024):>9.2f} "
            f"{statistics.mean(scores_2025):>9.2f} {u:>7.0f} {p:>7.4f}{sig} {cd.delta:>7.3f}"
        )

        table4["baseline_by_cohort"][d] = {
            "2024_mean": round(statistics.mean(scores_2024), 2),
            "2025_mean": round(statistics.mean(scores_2025), 2),
            "u_stat": round(u, 1),
            "p_value": round(p, 4),
            "cliffs_delta": cd.delta,
            "significant": p < 0.05,
        }

    results["table4_cross_cohort"] = table4

    # ---------------------------------------------------------------
    # 6. Additional analyses: per-ADR detail & distribution
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("ADDITIONAL: Score Distribution Analysis")
    print("=" * 70)

    # Score distribution for section-count baseline
    print("\nSection-count baseline score distribution per dimension:")
    print(f"{'Dimension':<25} {'Score 1':>8} {'Score 2':>8} {'Score 3':>8} {'Score 4':>8}")
    print("-" * 58)

    score_distributions = {}
    for d in DIMENSION_ORDER:
        scores = all_section_scores[d]
        counter = Counter(scores)
        dim = QUALITY_MODEL[d]

        dist = {s: counter.get(s, 0) for s in [1, 2, 3, 4]}
        dist_pct = {s: round(c / len(scores) * 100, 1) for s, c in dist.items()}
        score_distributions[d] = {"counts": dist, "percentages": dist_pct}

        print(
            f"{d} {dim.name:<22} "
            f"{dist[1]:>3} ({dist_pct[1]:>4.1f}%) "
            f"{dist[2]:>3} ({dist_pct[2]:>4.1f}%) "
            f"{dist[3]:>3} ({dist_pct[3]:>4.1f}%) "
            f"{dist[4]:>3} ({dist_pct[4]:>4.1f}%)"
        )

    results["score_distributions"] = score_distributions

    # Word-count baseline score distribution
    print("\nWord-count baseline score distribution per dimension:")
    print(f"{'Dimension':<25} {'Score 1':>8} {'Score 2':>8} {'Score 3':>8} {'Score 4':>8}")
    print("-" * 58)

    wc_score_distributions = {}
    for d in DIMENSION_ORDER:
        scores = all_word_scores[d]
        counter = Counter(scores)
        dim = QUALITY_MODEL[d]

        dist = {s: counter.get(s, 0) for s in [1, 2, 3, 4]}
        dist_pct = {s: round(c / len(scores) * 100, 1) for s, c in dist.items()}
        wc_score_distributions[d] = {"counts": dist, "percentages": dist_pct}

        print(
            f"{d} {dim.name:<22} "
            f"{dist[1]:>3} ({dist_pct[1]:>4.1f}%) "
            f"{dist[2]:>3} ({dist_pct[2]:>4.1f}%) "
            f"{dist[3]:>3} ({dist_pct[3]:>4.1f}%) "
            f"{dist[4]:>3} ({dist_pct[4]:>4.1f}%)"
        )

    results["wc_score_distributions"] = wc_score_distributions

    # ---------------------------------------------------------------
    # 7. Weakest/Strongest dimensions across corpus
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("ADDITIONAL: Weakest and Strongest Dimensions (Section-Count BL)")
    print("=" * 70)

    weakest_counts = Counter()
    strongest_counts = Counter()

    for r in section_results:
        weakest_counts[r.min_dimension] += 1
        strongest_counts[r.max_dimension] += 1

    print("\nMost frequently weakest dimension:")
    for dim_id, count in weakest_counts.most_common():
        dim = QUALITY_MODEL[dim_id]
        print(f"  {dim_id} {dim.name}: {count} ADRs ({count/len(adrs)*100:.1f}%)")

    print("\nMost frequently strongest dimension:")
    for dim_id, count in strongest_counts.most_common():
        dim = QUALITY_MODEL[dim_id]
        print(f"  {dim_id} {dim.name}: {count} ADRs ({count/len(adrs)*100:.1f}%)")

    results["weakest_dimensions"] = {
        k: {"count": v, "pct": round(v / len(adrs) * 100, 1)}
        for k, v in weakest_counts.most_common()
    }
    results["strongest_dimensions"] = {
        k: {"count": v, "pct": round(v / len(adrs) * 100, 1)}
        for k, v in strongest_counts.most_common()
    }

    # ---------------------------------------------------------------
    # 8. Category-level analysis
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("ADDITIONAL: Category-Level Quality (Section-Count BL)")
    print("=" * 70)

    cat_scores = {"structural": [], "content": [], "documentation": []}
    for r in section_results:
        for cat, score in r.category_scores.items():
            cat_scores[cat].append(score)

    print(f"\n{'Category':<25} {'Mean':>8} {'Std':>8} {'Median':>8}")
    print("-" * 50)
    for cat in ["structural", "content", "documentation"]:
        scores = cat_scores[cat]
        print(
            f"{cat.title():<25} {statistics.mean(scores):>8.2f} "
            f"{statistics.stdev(scores):>8.2f} {statistics.median(scores):>8.2f}"
        )

    results["category_analysis"] = {
        cat: {
            "mean": round(statistics.mean(scores), 2),
            "std": round(statistics.stdev(scores), 2),
            "median": round(statistics.median(scores), 2),
        }
        for cat, scores in cat_scores.items()
    }

    # ---------------------------------------------------------------
    # 9. Correlation between word count and section count
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("ADDITIONAL: Correlation Analysis")
    print("=" * 70)

    wc_arr = np.array(word_counts)
    sc_arr = np.array(total_counts)

    rho, p_corr = scipy_stats.spearmanr(wc_arr, sc_arr)
    print(f"\nWord count vs. section count: Spearman ρ={rho:.3f}, p={p_corr:.4f}")

    # Correlation between baselines
    s_comp = np.array([r.weighted_composite for r in section_results])
    w_comp = np.array([r.weighted_composite for r in word_results])
    rho_bl, p_bl = scipy_stats.spearmanr(s_comp, w_comp)
    print(f"Section BL vs. Word BL composites: Spearman ρ={rho_bl:.3f}, p={p_bl:.4f}")

    # Word count vs each baseline
    rho_wc_s, p_wc_s = scipy_stats.spearmanr(wc_arr, s_comp)
    rho_wc_w, p_wc_w = scipy_stats.spearmanr(wc_arr, w_comp)
    print(f"Word count vs. Section BL: Spearman ρ={rho_wc_s:.3f}, p={p_wc_s:.4f}")
    print(f"Word count vs. Word BL:    Spearman ρ={rho_wc_w:.3f}, p={p_wc_w:.4f}")

    results["correlations"] = {
        "word_count_vs_section_count": {"rho": round(rho, 3), "p": round(p_corr, 4)},
        "section_bl_vs_word_bl": {"rho": round(rho_bl, 3), "p": round(p_bl, 4)},
        "word_count_vs_section_bl": {"rho": round(rho_wc_s, 3), "p": round(p_wc_s, 4)},
        "word_count_vs_word_bl": {"rho": round(rho_wc_w, 3), "p": round(p_wc_w, 4)},
    }

    # ---------------------------------------------------------------
    # 10. Per-ADR detailed results
    # ---------------------------------------------------------------
    per_adr_results = []
    for i, (adr, sections) in enumerate(adr_sections):
        s_agg = section_results[i]
        w_agg = word_results[i]

        per_adr_results.append({
            "filename": adr.filename,
            "cohort": adr.cohort,
            "title": adr.title,
            "word_count": adr.word_count,
            "heading_count": adr.heading_count,
            "has_code_block": adr.has_code_block,
            "mandatory_sections": sections.mandatory_sections_present,
            "optional_sections": sections.optional_sections_present,
            "total_sections": sections.total_sections_present,
            "sections_present": {
                k: v is not None and len(str(v).strip()) > 0
                for k, v in sections.to_dict().items()
            },
            "section_baseline": {
                "scores": s_agg.dimension_scores,
                "composite": s_agg.weighted_composite,
                "tier": s_agg.tier.value,
                "category_scores": s_agg.category_scores,
            },
            "word_baseline": {
                "scores": w_agg.dimension_scores,
                "composite": w_agg.weighted_composite,
                "tier": w_agg.tier.value,
                "category_scores": w_agg.category_scores,
            },
        })

    results["per_adr_results"] = per_adr_results

    return results


if __name__ == "__main__":
    results = run_full_analysis()

    # Save full results to JSON
    output_path = Path("/home/user/adr-analyser/data/results/corpus_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n\nFull results saved to: {output_path}")
    print(f"Total entries in per-ADR results: {len(results['per_adr_results'])}")
