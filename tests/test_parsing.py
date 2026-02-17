"""Tests for ADR parsing and section extraction."""

import tempfile
from pathlib import Path

from adr_analyser.parsing.parser import parse_adr, parse_adr_directory
from adr_analyser.parsing.section_extractor import extract_sections


SAMPLE_ADR_FULL = """\
# ADR-005: Use gRPC for Inter-Service Communication

## Status
Accepted

## Date
2024-03-15

## Context and Problem Statement
Our microservices currently communicate via REST/JSON over HTTP/1.1.
As we scale to 15+ services, latency and payload overhead become significant.

## Decision Drivers
- Latency requirements: <50ms p99
- Strong typing across 3 language stacks

## Considered Options
1. REST/JSON (status quo)
2. gRPC with Protocol Buffers
3. Apache Thrift

## Decision Outcome
Chosen option: gRPC with Protocol Buffers, because it meets our latency requirements.

## Consequences
### Pros
- 3-10x reduction in serialization overhead
- Generated client/server stubs

### Cons
- Not human-readable on the wire
- Team needs Protocol Buffers training

## Links
- Related to ADR-003
"""

SAMPLE_ADR_MINIMAL = """\
# Use React

We decided to use React for the frontend.
"""

SAMPLE_ADR_NONSTANDARD = """\
# Using Bootstrap for Navigation

## Context
Need a navigation menu for our website.

## Issue
No experience in web design.

## Decision
Use Bootstrap.

## Solution
Leverage Bootstrap's pre-styled components.

## Rationale
Ease of use and responsiveness.

## Consequences
### Pros
- Rapid development
### Cons
- Dependency on Bootstrap
"""


def _write_temp_adr(content: str, name: str = "test_adr.md") -> Path:
    """Write ADR content to a temp file and return path."""
    tmp_dir = Path(tempfile.mkdtemp())
    adr_path = tmp_dir / "2024" / name
    adr_path.parent.mkdir(parents=True, exist_ok=True)
    adr_path.write_text(content)
    return adr_path


def test_parse_full_adr():
    """Parse a well-structured MADR-style ADR."""
    path = _write_temp_adr(SAMPLE_ADR_FULL)
    adr = parse_adr(path)

    assert adr.title == "ADR-005: Use gRPC for Inter-Service Communication"
    assert adr.metadata.status == "Accepted"
    assert adr.metadata.adr_id == "ADR-005"
    assert adr.cohort == "2024"
    assert adr.word_count > 50
    assert adr.heading_count >= 7


def test_parse_minimal_adr():
    """Parse a minimal ADR with just a title and one sentence."""
    path = _write_temp_adr(SAMPLE_ADR_MINIMAL, "minimal.md")
    adr = parse_adr(path)

    assert adr.title == "Use React"
    assert adr.word_count < 20


def test_extract_sections_full():
    """Extract sections from a well-structured ADR."""
    path = _write_temp_adr(SAMPLE_ADR_FULL)
    adr = parse_adr(path)
    sections = extract_sections(adr)

    assert sections.context is not None
    assert "microservices" in sections.context
    assert sections.decision_drivers is not None
    assert sections.considered_options is not None
    assert sections.decision_outcome is not None
    assert sections.pros is not None
    assert sections.cons is not None
    assert sections.status == "Accepted"
    assert sections.mandatory_sections_present >= 2


def test_extract_sections_minimal():
    """Extract sections from a minimal ADR."""
    path = _write_temp_adr(SAMPLE_ADR_MINIMAL, "minimal.md")
    adr = parse_adr(path)
    sections = extract_sections(adr)

    # Minimal ADR has almost no recognizable sections
    assert sections.mandatory_sections_present <= 1


def test_extract_sections_nonstandard():
    """Extract sections from a non-standard ADR (with Issue/Solution)."""
    path = _write_temp_adr(SAMPLE_ADR_NONSTANDARD, "nonstandard.md")
    adr = parse_adr(path)
    sections = extract_sections(adr)

    assert sections.context is not None
    assert sections.issue is not None
    assert sections.decision is not None
    assert sections.solution is not None
    assert sections.rationale is not None


def test_pros_cons_extraction():
    """Pros and cons should be extracted from within Consequences."""
    path = _write_temp_adr(SAMPLE_ADR_FULL)
    adr = parse_adr(path)
    sections = extract_sections(adr)

    assert sections.pros is not None
    assert "serialization" in sections.pros
    assert sections.cons is not None
    assert "human-readable" in sections.cons


def test_parse_directory():
    """parse_adr_directory should find and parse all ADRs."""
    tmp_dir = Path(tempfile.mkdtemp())
    (tmp_dir / "2024").mkdir()
    (tmp_dir / "2024" / "adr1.md").write_text(SAMPLE_ADR_FULL)
    (tmp_dir / "2024" / "adr2.md").write_text(SAMPLE_ADR_MINIMAL)
    (tmp_dir / "plan.md").write_text("# Plan\nNot an ADR")

    adrs = parse_adr_directory(tmp_dir)
    assert len(adrs) == 2  # plan.md should be skipped


def test_parse_real_adrs():
    """Parse the actual ADR dataset to verify robustness."""
    adr_dir = Path("/home/user/adr-analyser/adrs")
    if not adr_dir.exists():
        return  # Skip if not in expected environment

    adrs = parse_adr_directory(adr_dir)
    assert len(adrs) >= 100  # We expect ~110 ADRs

    # Every ADR should parse without error and have some content
    for adr in adrs:
        assert adr.word_count > 0
        assert adr.title
        sections = extract_sections(adr)
        # At least some sections should be extractable from most ADRs
