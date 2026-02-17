"""
CLI entry point for the ADR Analyser pipeline.

Usage:
    adr-analyse parse <directory>          Parse ADRs and extract sections
    adr-analyse score <directory>          Score ADRs using LLM
    adr-analyse batch-input <directory>    Generate batch input JSONL
    adr-analyse feedback <results.json>    Generate feedback reports
    adr-analyse evaluate <results> <gt>    Run evaluation metrics
    adr-analyse baseline <directory>       Run non-LLM baselines
    adr-analyse stats <directory>          Print dataset statistics
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click


@click.group()
@click.version_option(version="0.1.0")
def main():
    """ADR Analyser: Automated ADR quality assessment with LLMs."""
    pass


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None, help="Output JSON file")
def parse(directory: str, output: str | None):
    """Parse ADRs and extract sections from a directory."""
    from adr_analyser.parsing.parser import parse_adr_directory
    from adr_analyser.parsing.section_extractor import extract_sections

    adrs = parse_adr_directory(directory)
    click.echo(f"Parsed {len(adrs)} ADRs from {directory}")

    results = []
    for adr in adrs:
        sections = extract_sections(adr)
        result = {
            "filename": adr.filename,
            "cohort": adr.cohort,
            "title": adr.title,
            "word_count": adr.word_count,
            "heading_count": adr.heading_count,
            "has_code_block": adr.has_code_block,
            "metadata": {
                "status": adr.metadata.status,
                "date": adr.metadata.date,
                "deciders": adr.metadata.deciders,
                "adr_id": adr.metadata.adr_id,
            },
            "sections": sections.to_dict(),
            "mandatory_sections_present": sections.mandatory_sections_present,
            "optional_sections_present": sections.optional_sections_present,
        }
        results.append(result)

    if output:
        Path(output).write_text(json.dumps(results, indent=2, ensure_ascii=False))
        click.echo(f"Results written to {output}")
    else:
        # Print summary table
        click.echo(f"\n{'Filename':<60} {'Cohort':<6} {'Words':<6} {'Sections':<8}")
        click.echo("-" * 80)
        for r in results:
            total_sections = r["mandatory_sections_present"] + r["optional_sections_present"]
            click.echo(
                f"{r['filename']:<60} {r['cohort']:<6} "
                f"{r['word_count']:<6} {total_sections:<8}"
            )


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), required=True, help="Output JSONL file")
@click.option("--model", "-m", default="gemini-2.0-flash", help="Gemini model name")
@click.option("--passes", "-p", default=5, type=int, help="Number of inference passes")
def batch_input(directory: str, output: str, model: str, passes: int):
    """Generate batch input JSONL for Vertex AI Batch Prediction."""
    from adr_analyser.parsing.parser import parse_adr_directory
    from adr_analyser.scoring.gemini_scorer import GeminiScorer

    adrs = parse_adr_directory(directory)
    click.echo(f"Parsed {len(adrs)} ADRs")

    scorer = GeminiScorer(model_name=model, num_passes=passes)
    adr_pairs = [(adr.filename, adr.body) for adr in adrs]
    output_path = scorer.generate_batch_input(adr_pairs, output)
    click.echo(f"Batch input written to {output_path}")


@main.command()
@click.argument("directory", type=click.Path(exists=True))
def stats(directory: str):
    """Print dataset statistics for the ADR corpus."""
    from adr_analyser.parsing.parser import parse_adr_directory
    from adr_analyser.parsing.section_extractor import extract_sections

    adrs = parse_adr_directory(directory)
    click.echo(f"\nDataset Statistics for {directory}")
    click.echo("=" * 50)
    click.echo(f"Total ADRs: {len(adrs)}")

    # By cohort
    cohorts = {}
    for adr in adrs:
        cohorts.setdefault(adr.cohort, []).append(adr)

    click.echo(f"\nBy cohort:")
    for cohort, items in sorted(cohorts.items()):
        click.echo(f"  {cohort}: {len(items)} ADRs")

    # Word count statistics
    word_counts = [adr.word_count for adr in adrs]
    click.echo(f"\nWord count:")
    click.echo(f"  Mean: {sum(word_counts) / len(word_counts):.0f}")
    click.echo(f"  Min:  {min(word_counts)}")
    click.echo(f"  Max:  {max(word_counts)}")

    # Section statistics
    section_counts = []
    for adr in adrs:
        sections = extract_sections(adr)
        section_counts.append(sections.total_sections_present)

    click.echo(f"\nSection count:")
    click.echo(f"  Mean: {sum(section_counts) / len(section_counts):.1f}")
    click.echo(f"  Min:  {min(section_counts)}")
    click.echo(f"  Max:  {max(section_counts)}")

    # Metadata presence
    has_status = sum(1 for adr in adrs if adr.metadata.status)
    has_date = sum(1 for adr in adrs if adr.metadata.date)
    click.echo(f"\nMetadata presence:")
    click.echo(f"  Has status: {has_status}/{len(adrs)} ({has_status/len(adrs)*100:.0f}%)")
    click.echo(f"  Has date:   {has_date}/{len(adrs)} ({has_date/len(adrs)*100:.0f}%)")

    # Code block presence
    has_code = sum(1 for adr in adrs if adr.has_code_block)
    click.echo(f"  Has code:   {has_code}/{len(adrs)} ({has_code/len(adrs)*100:.0f}%)")


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None, help="Output JSON file")
def baseline(directory: str, output: str | None):
    """Run non-LLM baselines (section-count and word-count heuristics)."""
    from adr_analyser.baselines.non_llm import SectionCountBaseline, WordCountBaseline
    from adr_analyser.parsing.parser import parse_adr_directory
    from adr_analyser.aggregation.aggregator import aggregate_scores

    adrs = parse_adr_directory(directory)
    click.echo(f"Running baselines on {len(adrs)} ADRs")

    section_bl = SectionCountBaseline()
    word_bl = WordCountBaseline()

    results = []
    for adr in adrs:
        section_scores = section_bl.predict(adr)
        word_scores = word_bl.predict(adr)

        section_agg = aggregate_scores(adr.filename, section_scores)
        word_agg = aggregate_scores(adr.filename, word_scores)

        results.append({
            "filename": adr.filename,
            "cohort": adr.cohort,
            "section_count_baseline": {
                "scores": section_scores,
                "composite": section_agg.weighted_composite,
                "tier": section_agg.tier.value,
            },
            "word_count_baseline": {
                "scores": word_scores,
                "composite": word_agg.weighted_composite,
                "tier": word_agg.tier.value,
            },
        })

    if output:
        Path(output).write_text(json.dumps(results, indent=2))
        click.echo(f"Results written to {output}")
    else:
        click.echo(f"\n{'Filename':<50} {'Section BL':<12} {'Word BL':<12}")
        click.echo("-" * 74)
        for r in results:
            click.echo(
                f"{r['filename']:<50} "
                f"{r['section_count_baseline']['composite']:<12.2f} "
                f"{r['word_count_baseline']['composite']:<12.2f}"
            )


if __name__ == "__main__":
    main()
