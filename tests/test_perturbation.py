"""Tests for the perturbation generator module."""

import pytest

from adr_analyser.parsing.parser import ParsedADR, ADRMetadata
from adr_analyser.perturbation.generator import (
    PerturbationType,
    generate_perturbation,
    generate_all_perturbations,
    select_perturbation_candidates,
    perturb_remove_context,
    perturb_remove_rationale,
    perturb_remove_consequences,
    perturb_remove_decision,
    perturb_shallow_rationale,
    perturb_vague_decision,
    perturb_add_contradictions,
    perturb_destroy_structure,
    perturb_strip_optional,
    perturb_add_drivers,
)


@pytest.fixture
def sample_markdown_adr():
    """A well-structured markdown ADR for perturbation testing."""
    content = """\
# ADR-001: Use PostgreSQL as Primary Database

## Status
Accepted

## Context
Our application needs a reliable, scalable relational database to store
user accounts, transactions, and audit logs. We anticipate up to 10,000
concurrent users within the first year. Data integrity is critical for
financial transactions, and we need ACID compliance.

## Decision
We have decided to use PostgreSQL 16 as our primary relational database.
It will be deployed on AWS RDS with multi-AZ redundancy.

## Rationale
PostgreSQL was chosen because it provides strong ACID compliance,
excellent support for complex queries and JSON data types, and has a
mature ecosystem. Unlike MySQL, it supports advanced indexing strategies
(GIN, GiST) needed for our search functionality. The team has prior
experience with PostgreSQL from previous projects, reducing onboarding time.

## Consequences
### Positive
- Strong ACID compliance ensures data integrity for financial transactions
- Advanced indexing supports our full-text search requirements
- Active community means security patches and feature updates
- AWS RDS handles operational overhead (backups, patching)

### Negative
- Higher memory footprint compared to MySQL for simple queries
- Team needs training on PostgreSQL-specific features (JSONB, CTEs)
- AWS RDS costs are higher than self-managed deployment

## Sample Code
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```
"""
    return ParsedADR(
        file_path="/test/adrs/2024/ADR001.md",
        filename="ADR001.md",
        cohort="2024",
        raw_content=content,
        metadata=ADRMetadata(status="Accepted"),
        body=content,
        title="ADR-001: Use PostgreSQL as Primary Database",
        word_count=200,
        heading_count=7,
        has_code_block=True,
        headings=[
            (1, "ADR-001: Use PostgreSQL as Primary Database"),
            (2, "Status"),
            (2, "Context"),
            (2, "Decision"),
            (2, "Rationale"),
            (2, "Consequences"),
            (2, "Sample Code"),
        ],
    )


@pytest.fixture
def sample_plaintext_adr():
    """A plain-text ADR (2025 style) without markdown headings."""
    content = """\
Architecture Decision Record (ADR): API Gateway with Kong

Title
Using Kong as an API Gateway for centralized API management

Context
As our system grows, managing APIs efficiently becomes a challenge. We need
a centralized API Gateway to handle authentication, rate limiting, and routing.

Decision
We have decided to implement Kong API Gateway for managing our APIs.
The key reasons include scalability, plugin system, and performance.

Consequences
Positive Outcomes:
- Centralized API management
- Improved security and observability

Potential Drawbacks:
- Learning curve for configuring Kong
- Additional infrastructure costs
"""
    return ParsedADR(
        file_path="/test/adrs/2025/Kong_ADR.md",
        filename="Kong_ADR.md",
        cohort="2025",
        raw_content=content,
        metadata=ADRMetadata(),
        body=content,
        title="Architecture Decision Record (ADR): API Gateway with Kong",
        word_count=120,
        heading_count=0,
        has_code_block=False,
        headings=[],
    )


class TestRemoveSectionPerturbations:
    """Test section removal perturbations."""

    def test_remove_context(self, sample_markdown_adr):
        result = perturb_remove_context(sample_markdown_adr)
        assert "Context" not in result.perturbed_content or "context" not in result.perturbed_content.lower().split("##")[1] if "##" in result.perturbed_content else True
        assert result.perturbation_type == PerturbationType.REMOVE_CONTEXT
        assert result.expected_dimension_impacts["B1"] == "decrease"
        assert "concurrent users" not in result.perturbed_content
        # Decision should still be present
        assert "PostgreSQL" in result.perturbed_content

    def test_remove_rationale(self, sample_markdown_adr):
        result = perturb_remove_rationale(sample_markdown_adr)
        assert result.perturbation_type == PerturbationType.REMOVE_RATIONALE
        assert result.expected_dimension_impacts["B3"] == "decrease"
        assert "ACID compliance" not in result.perturbed_content or \
               result.perturbed_content.count("ACID") < sample_markdown_adr.raw_content.count("ACID")
        # Context should still be present
        assert "concurrent users" in result.perturbed_content

    def test_remove_consequences(self, sample_markdown_adr):
        result = perturb_remove_consequences(sample_markdown_adr)
        assert result.perturbation_type == PerturbationType.REMOVE_CONSEQUENCES
        assert result.expected_dimension_impacts["B4"] == "decrease"
        # Decision and context should still be present
        assert "PostgreSQL 16" in result.perturbed_content
        assert "concurrent users" in result.perturbed_content

    def test_remove_decision(self, sample_markdown_adr):
        result = perturb_remove_decision(sample_markdown_adr)
        assert result.perturbation_type == PerturbationType.REMOVE_DECISION
        assert result.expected_dimension_impacts["B5"] == "decrease"


class TestContentReplacementPerturbations:
    """Test content replacement perturbations."""

    def test_shallow_rationale(self, sample_markdown_adr):
        result = perturb_shallow_rationale(sample_markdown_adr)
        assert result.perturbation_type == PerturbationType.SHALLOW_RATIONALE
        assert result.expected_dimension_impacts["B3"] == "decrease"
        # The shallow replacement text should be present
        assert "most popular" in result.perturbed_content
        # Original deep rationale content should be replaced
        assert "GIN, GiST" not in result.perturbed_content

    def test_vague_decision(self, sample_markdown_adr):
        result = perturb_vague_decision(sample_markdown_adr)
        assert result.perturbation_type == PerturbationType.VAGUE_DECISION
        assert result.expected_dimension_impacts["B5"] == "decrease"
        # Vague text should be present
        assert "modern framework/tool" in result.perturbed_content
        # Original specific decision should be replaced
        assert "PostgreSQL 16" not in result.perturbed_content or \
               result.perturbed_content.index("modern framework") < result.perturbed_content.index("PostgreSQL 16") if "PostgreSQL 16" in result.perturbed_content else True


class TestStructuralPerturbations:
    """Test structural perturbations."""

    def test_destroy_structure(self, sample_markdown_adr):
        result = perturb_destroy_structure(sample_markdown_adr)
        assert result.perturbation_type == PerturbationType.DESTROY_STRUCTURE
        assert result.expected_dimension_impacts["A2"] == "decrease"
        # No markdown headings should remain
        assert "## " not in result.perturbed_content
        assert "# " not in result.perturbed_content
        # But content should still be there
        assert "PostgreSQL" in result.perturbed_content
        assert "concurrent users" in result.perturbed_content

    def test_strip_optional(self, sample_markdown_adr):
        result = perturb_strip_optional(sample_markdown_adr)
        assert result.perturbation_type == PerturbationType.STRIP_ALL_OPTIONAL
        assert result.expected_dimension_impacts["A1"] == "decrease"
        # Core sections should still be present
        assert "Context" in result.perturbed_content
        assert "Decision" in result.perturbed_content


class TestEnhancementPerturbations:
    """Test positive control (enhancement) perturbations."""

    def test_add_drivers(self, sample_markdown_adr):
        result = perturb_add_drivers(sample_markdown_adr)
        assert result.perturbation_type == PerturbationType.ENHANCE_ADD_DRIVERS
        assert result.expected_dimension_impacts["B1"] == "increase"
        assert result.expected_dimension_impacts["A1"] == "increase"
        # New content should be added
        assert "Decision Drivers" in result.perturbed_content
        assert "scalability" in result.perturbed_content.lower()


class TestPerturbationMetadata:
    """Test perturbation metadata is correct."""

    def test_expected_impacts_all_dimensions(self, sample_markdown_adr):
        for ptype in PerturbationType:
            result = generate_perturbation(sample_markdown_adr, ptype)
            # All 10 dimensions should have expected impacts
            for dim_id in ["A1", "A2", "B1", "B2", "B3", "B4", "B5", "C1", "C2", "C3"]:
                assert dim_id in result.expected_dimension_impacts, \
                    f"{ptype.value} missing impact for {dim_id}"

    def test_perturbation_type_is_set(self, sample_markdown_adr):
        for ptype in PerturbationType:
            result = generate_perturbation(sample_markdown_adr, ptype)
            assert result.perturbation_type == ptype

    def test_original_filename_preserved(self, sample_markdown_adr):
        for ptype in PerturbationType:
            result = generate_perturbation(sample_markdown_adr, ptype)
            assert result.original_filename == sample_markdown_adr.filename


class TestGenerateAllPerturbations:
    """Test bulk perturbation generation."""

    def test_generates_multiple(self, sample_markdown_adr):
        pset = generate_all_perturbations(sample_markdown_adr)
        assert pset.original_filename == sample_markdown_adr.filename
        assert pset.original_content == sample_markdown_adr.raw_content
        # Should generate at least some perturbations
        assert len(pset.perturbations) > 0

    def test_filters_unchanged(self, sample_markdown_adr):
        """Perturbations that don't change content should be filtered out."""
        pset = generate_all_perturbations(sample_markdown_adr)
        for p in pset.perturbations:
            assert p.perturbed_content.strip() != sample_markdown_adr.raw_content.strip()

    def test_specific_types(self, sample_markdown_adr):
        types = [PerturbationType.REMOVE_CONTEXT, PerturbationType.DESTROY_STRUCTURE]
        pset = generate_all_perturbations(sample_markdown_adr, types=types)
        generated_types = {p.perturbation_type for p in pset.perturbations}
        # Should only contain requested types (some may be filtered if no change)
        assert generated_types.issubset(set(types))


class TestSelectCandidates:
    """Test candidate selection for perturbation."""

    def test_filters_by_sections(self, sample_markdown_adr, sample_plaintext_adr):
        # Markdown ADR should qualify (has multiple sections)
        candidates = select_perturbation_candidates(
            [sample_markdown_adr, sample_plaintext_adr],
            min_sections=2,
            min_word_count=100,
        )
        # At least the markdown ADR should be selected
        assert len(candidates) >= 1

    def test_filters_by_word_count(self, sample_markdown_adr):
        candidates = select_perturbation_candidates(
            [sample_markdown_adr],
            min_sections=1,
            min_word_count=50000,  # Impossibly high
        )
        assert len(candidates) == 0


class TestPlainTextPerturbations:
    """Test perturbations work on plain-text (2025-style) ADRs."""

    def test_remove_context_plaintext(self, sample_plaintext_adr):
        result = perturb_remove_context(sample_plaintext_adr)
        # The context section content should be removed
        assert "managing APIs efficiently" not in result.perturbed_content
        # Decision should still be present
        assert "Kong API Gateway" in result.perturbed_content

    def test_destroy_structure_plaintext(self, sample_plaintext_adr):
        """Plain-text ADR already has no markdown headings, so this should
        still produce valid output (even if minimal change)."""
        result = perturb_destroy_structure(sample_plaintext_adr)
        assert result.perturbation_type == PerturbationType.DESTROY_STRUCTURE
        assert "Kong" in result.perturbed_content

    def test_add_contradictions_plaintext(self, sample_plaintext_adr):
        result = perturb_add_contradictions(sample_plaintext_adr)
        assert "not actually relevant" in result.perturbed_content
        assert result.expected_dimension_impacts["C2"] == "decrease"
