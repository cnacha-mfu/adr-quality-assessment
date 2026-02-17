"""
Perturbation Generator for controlled ADR quality degradation (RQ3).

Creates systematic, repeatable perturbations of real ADRs to validate
that LLM scorers are sensitive to genuine quality differences.

Perturbation types and their expected dimension impacts:
1. remove_context      -> B1 (Context Adequacy) should drop
2. remove_rationale    -> B3 (Rationale Depth) should drop
3. remove_consequences -> B4 (Consequence Specificity) should drop
4. remove_decision     -> B5 (Decision Specificity) should drop
5. shallow_rationale   -> B3 (Rationale Depth) should drop
6. vague_decision      -> B5 (Decision Specificity) should drop
7. add_contradictions  -> C2 (Consistency) should drop
8. destroy_structure   -> A2 (Structural Conformance) should drop
9. strip_all_optional  -> A1 (Completeness) should drop
10. enhance_add_drivers -> B1 should improve (positive control)

Each perturbation is deterministic given the same input ADR.
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from adr_analyser.parsing.parser import ParsedADR
from adr_analyser.parsing.section_extractor import ExtractedSections, extract_sections


class PerturbationType(str, Enum):
    """Types of controlled perturbation."""

    REMOVE_CONTEXT = "remove_context"
    REMOVE_RATIONALE = "remove_rationale"
    REMOVE_CONSEQUENCES = "remove_consequences"
    REMOVE_DECISION = "remove_decision"
    SHALLOW_RATIONALE = "shallow_rationale"
    VAGUE_DECISION = "vague_decision"
    ADD_CONTRADICTIONS = "add_contradictions"
    DESTROY_STRUCTURE = "destroy_structure"
    STRIP_ALL_OPTIONAL = "strip_all_optional"
    ENHANCE_ADD_DRIVERS = "enhance_add_drivers"


@dataclass
class PerturbedADR:
    """An ADR that has been systematically perturbed."""

    original_filename: str
    perturbation_type: PerturbationType
    perturbed_content: str
    expected_dimension_impacts: dict[str, str]  # dim_id -> "decrease" | "increase" | "unchanged"
    description: str  # Human-readable description of what was changed
    sections_modified: list[str]  # List of section names that were modified


@dataclass
class PerturbationSet:
    """A complete set of perturbations for one ADR."""

    original_filename: str
    original_content: str
    perturbations: list[PerturbedADR] = field(default_factory=list)


# Expected dimension impacts for each perturbation type
_EXPECTED_IMPACTS: dict[PerturbationType, dict[str, str]] = {
    PerturbationType.REMOVE_CONTEXT: {
        "A1": "decrease", "B1": "decrease",
        "B2": "unchanged", "B3": "unchanged", "B4": "unchanged",
        "B5": "unchanged", "C1": "unchanged", "C2": "unchanged",
        "C3": "unchanged", "A2": "unchanged",
    },
    PerturbationType.REMOVE_RATIONALE: {
        "A1": "decrease", "B3": "decrease",
        "B1": "unchanged", "B2": "unchanged", "B4": "unchanged",
        "B5": "unchanged", "C1": "unchanged", "C2": "unchanged",
        "C3": "unchanged", "A2": "unchanged",
    },
    PerturbationType.REMOVE_CONSEQUENCES: {
        "A1": "decrease", "B4": "decrease",
        "B1": "unchanged", "B2": "unchanged", "B3": "unchanged",
        "B5": "unchanged", "C1": "unchanged", "C2": "unchanged",
        "C3": "unchanged", "A2": "unchanged",
    },
    PerturbationType.REMOVE_DECISION: {
        "A1": "decrease", "B5": "decrease",
        "B1": "unchanged", "B2": "unchanged", "B3": "unchanged",
        "B4": "unchanged", "C1": "unchanged", "C2": "unchanged",
        "C3": "unchanged", "A2": "unchanged",
    },
    PerturbationType.SHALLOW_RATIONALE: {
        "B3": "decrease",
        "A1": "unchanged", "A2": "unchanged", "B1": "unchanged",
        "B2": "unchanged", "B4": "unchanged", "B5": "unchanged",
        "C1": "unchanged", "C2": "unchanged", "C3": "unchanged",
    },
    PerturbationType.VAGUE_DECISION: {
        "B5": "decrease",
        "A1": "unchanged", "A2": "unchanged", "B1": "unchanged",
        "B2": "unchanged", "B3": "unchanged", "B4": "unchanged",
        "C1": "unchanged", "C2": "unchanged", "C3": "unchanged",
    },
    PerturbationType.ADD_CONTRADICTIONS: {
        "C2": "decrease",
        "A1": "unchanged", "A2": "unchanged", "B1": "unchanged",
        "B2": "unchanged", "B3": "unchanged", "B4": "unchanged",
        "B5": "unchanged", "C1": "unchanged", "C3": "unchanged",
    },
    PerturbationType.DESTROY_STRUCTURE: {
        "A2": "decrease",
        "A1": "decrease",
        "B1": "unchanged", "B2": "unchanged", "B3": "unchanged",
        "B4": "unchanged", "B5": "unchanged", "C1": "unchanged",
        "C2": "unchanged", "C3": "unchanged",
    },
    PerturbationType.STRIP_ALL_OPTIONAL: {
        "A1": "decrease",
        "A2": "unchanged", "B1": "unchanged", "B2": "unchanged",
        "B3": "unchanged", "B4": "decrease", "B5": "unchanged",
        "C1": "unchanged", "C2": "unchanged", "C3": "unchanged",
    },
    PerturbationType.ENHANCE_ADD_DRIVERS: {
        "B1": "increase", "A1": "increase",
        "A2": "unchanged", "B2": "unchanged", "B3": "unchanged",
        "B4": "unchanged", "B5": "unchanged", "C1": "unchanged",
        "C2": "unchanged", "C3": "unchanged",
    },
}


def _remove_section_by_heading(content: str, section_keywords: list[str]) -> str:
    """Remove a section from ADR content by matching heading keywords.

    Handles both markdown headings (## Section) and plain-text headings (Section).
    Removes everything from the matched heading to the next heading of same or higher level.
    """
    lines = content.splitlines(keepends=True)
    result_lines = []
    skip = False
    skip_level = 0

    # Compile keyword patterns for sections to remove
    keyword_patterns = [
        re.compile(rf"\b{kw}\b", re.IGNORECASE) for kw in section_keywords
    ]

    md_heading_re = re.compile(r"^(#{1,6})\s+(.+)$")

    # General plain-text heading detector (all known section names)
    # Used to detect section boundaries, not just the target sections
    _ALL_SECTION_NAMES = (
        r"Context|Problem\s+Statement|Background|Motivation|"
        r"Decision|Chosen\s+Option|Selected\s+Option|"
        r"Decision\s+Drivers?|Considered\s+Options?|Alternatives?|"
        r"Rationale|Justification|Reasoning|Why|"
        r"Consequences?|Impact|Implications?|Pros?\s+(?:and|&)\s+Cons?|"
        r"Positive|Negative|Pros?|Cons?|Advantages?|Disadvantages?|"
        r"Confirmation|More\s+Information|References?|Links?|"
        r"Status|Date|Deciders?|Title|"
        r"Sample\s+Code|Code\s+Example|Solution|Approach"
    )
    any_heading_re = re.compile(
        rf"^({_ALL_SECTION_NAMES})\s*:?\s*$",
        re.IGNORECASE,
    )

    for line in lines:
        stripped = line.strip()

        # Check for markdown heading
        md_match = md_heading_re.match(stripped)
        if md_match:
            level = len(md_match.group(1))
            heading_text = md_match.group(2)

            if skip and level <= skip_level:
                skip = False  # New section at same or higher level ends removal

            if not skip:
                # Check if this heading matches a section to remove
                for pat in keyword_patterns:
                    if pat.search(heading_text):
                        skip = True
                        skip_level = level
                        break

            if not skip:
                result_lines.append(line)
            continue

        # Check for plain-text heading (any known section name)
        if any_heading_re.match(stripped):
            if skip:
                # Any new section heading ends the removal
                skip = False

            if not skip:
                # Check if this heading matches a section to remove
                for pat in keyword_patterns:
                    if pat.search(stripped):
                        skip = True
                        skip_level = 2  # Treat plain-text headings as level 2
                        break

            if not skip:
                result_lines.append(line)
            continue

        if not skip:
            result_lines.append(line)

    return "".join(result_lines)


def _replace_section_content(
    content: str,
    section_keywords: list[str],
    replacement: str,
) -> str:
    """Replace the content of a section while keeping its heading.

    Handles both markdown and plain-text headings.
    """
    lines = content.splitlines(keepends=True)
    result_lines = []
    in_target = False
    replaced = False
    target_level = 0

    keyword_patterns = [
        re.compile(rf"\b{kw}\b", re.IGNORECASE) for kw in section_keywords
    ]

    md_heading_re = re.compile(r"^(#{1,6})\s+(.+)$")

    # General plain-text heading detector (all known section names)
    _ALL_SECTION_NAMES = (
        r"Context|Problem\s+Statement|Background|Motivation|"
        r"Decision|Chosen\s+Option|Selected\s+Option|"
        r"Decision\s+Drivers?|Considered\s+Options?|Alternatives?|"
        r"Rationale|Justification|Reasoning|Why|"
        r"Consequences?|Impact|Implications?|Pros?\s+(?:and|&)\s+Cons?|"
        r"Positive|Negative|Pros?|Cons?|Advantages?|Disadvantages?|"
        r"Confirmation|More\s+Information|References?|Links?|"
        r"Status|Date|Deciders?|Title|"
        r"Sample\s+Code|Code\s+Example|Solution|Approach"
    )
    any_heading_re = re.compile(
        rf"^({_ALL_SECTION_NAMES})\s*:?\s*$",
        re.IGNORECASE,
    )

    for line in lines:
        stripped = line.strip()

        md_match = md_heading_re.match(stripped)
        if md_match:
            level = len(md_match.group(1))
            heading_text = md_match.group(2)

            if in_target and level <= target_level:
                in_target = False

            if not in_target and not replaced:
                for pat in keyword_patterns:
                    if pat.search(heading_text):
                        in_target = True
                        target_level = level
                        result_lines.append(line)
                        result_lines.append(replacement + "\n\n")
                        replaced = True
                        break
                else:
                    result_lines.append(line)
            elif not in_target:
                result_lines.append(line)
            continue

        if any_heading_re.match(stripped):
            if in_target:
                in_target = False

            if not in_target and not replaced:
                for pat in keyword_patterns:
                    if pat.search(stripped):
                        in_target = True
                        target_level = 2
                        result_lines.append(line)
                        result_lines.append(replacement + "\n\n")
                        replaced = True
                        break
                else:
                    result_lines.append(line)
            elif not in_target:
                result_lines.append(line)
            continue

        if not in_target:
            result_lines.append(line)

    return "".join(result_lines)


def _insert_after_section(
    content: str,
    after_keywords: list[str],
    heading: str,
    new_content: str,
) -> str:
    """Insert a new section after a specified section."""
    lines = content.splitlines(keepends=True)
    result_lines = []
    in_target = False
    inserted = False
    target_level = 0

    keyword_patterns = [
        re.compile(rf"\b{kw}\b", re.IGNORECASE) for kw in after_keywords
    ]
    md_heading_re = re.compile(r"^(#{1,6})\s+(.+)$")

    for i, line in enumerate(lines):
        stripped = line.strip()
        md_match = md_heading_re.match(stripped)

        if md_match:
            level = len(md_match.group(1))
            heading_text = md_match.group(2)

            if in_target and level <= target_level and not inserted:
                # End of target section: insert here
                result_lines.append(f"\n{'#' * target_level} {heading}\n")
                result_lines.append(new_content + "\n\n")
                inserted = True
                in_target = False

            if not in_target:
                for pat in keyword_patterns:
                    if pat.search(heading_text):
                        in_target = True
                        target_level = level
                        break

        result_lines.append(line)

    # If target was last section, append at end
    if in_target and not inserted:
        result_lines.append(f"\n{'#' * target_level} {heading}\n")
        result_lines.append(new_content + "\n\n")

    return "".join(result_lines)


def perturb_remove_context(adr: ParsedADR) -> PerturbedADR:
    """Remove the context/problem statement section entirely."""
    content = _remove_section_by_heading(
        adr.raw_content,
        ["Context", "Problem Statement", "Background", "Motivation"],
    )
    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.REMOVE_CONTEXT,
        perturbed_content=content,
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.REMOVE_CONTEXT],
        description="Removed context/problem statement section entirely",
        sections_modified=["context"],
    )


def perturb_remove_rationale(adr: ParsedADR) -> PerturbedADR:
    """Remove the rationale/justification section entirely."""
    content = _remove_section_by_heading(
        adr.raw_content,
        ["Rationale", "Justification", "Reasoning", "Why"],
    )
    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.REMOVE_RATIONALE,
        perturbed_content=content,
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.REMOVE_RATIONALE],
        description="Removed rationale/justification section entirely",
        sections_modified=["rationale"],
    )


def perturb_remove_consequences(adr: ParsedADR) -> PerturbedADR:
    """Remove the consequences section entirely."""
    content = _remove_section_by_heading(
        adr.raw_content,
        ["Consequences", "Impact", "Implications", "Pros and Cons"],
    )
    # Also remove standalone Pros/Cons sections
    content = _remove_section_by_heading(
        content,
        ["Positive", "Negative", "Pros", "Cons", "Advantages", "Disadvantages"],
    )
    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.REMOVE_CONSEQUENCES,
        perturbed_content=content,
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.REMOVE_CONSEQUENCES],
        description="Removed consequences/pros/cons sections entirely",
        sections_modified=["consequences", "pros", "cons"],
    )


def perturb_remove_decision(adr: ParsedADR) -> PerturbedADR:
    """Remove the decision section entirely."""
    content = _remove_section_by_heading(
        adr.raw_content,
        ["Decision", "Chosen Option", "Selected Option"],
    )
    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.REMOVE_DECISION,
        perturbed_content=content,
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.REMOVE_DECISION],
        description="Removed decision section entirely",
        sections_modified=["decision"],
    )


def perturb_shallow_rationale(adr: ParsedADR) -> PerturbedADR:
    """Replace rationale with a generic, shallow version."""
    shallow = (
        "We chose this option because it is the most popular and well-supported choice. "
        "It seemed like the best fit for our needs."
    )
    content = _replace_section_content(
        adr.raw_content,
        ["Rationale", "Justification", "Reasoning", "Why"],
        shallow,
    )
    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.SHALLOW_RATIONALE,
        perturbed_content=content,
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.SHALLOW_RATIONALE],
        description="Replaced rationale with generic shallow justification",
        sections_modified=["rationale"],
    )


def perturb_vague_decision(adr: ParsedADR) -> PerturbedADR:
    """Replace the decision with a vague, non-specific statement."""
    vague = (
        "We decided to use a modern framework/tool that addresses our requirements. "
        "The specific approach will be determined during implementation."
    )
    content = _replace_section_content(
        adr.raw_content,
        ["Decision", "Chosen Option", "Selected Option"],
        vague,
    )
    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.VAGUE_DECISION,
        perturbed_content=content,
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.VAGUE_DECISION],
        description="Replaced decision with vague non-specific statement",
        sections_modified=["decision"],
    )


def perturb_add_contradictions(adr: ParsedADR) -> PerturbedADR:
    """Add contradictory statements between sections.

    Inserts a statement in the consequences section that directly
    contradicts the context section's stated requirements.
    """
    sections = extract_sections(adr)

    # Find what the context says is important and contradict it
    contradiction = (
        "\n\nNote: After further analysis, we found that the requirements "
        "described in the context section are not actually relevant to our project. "
        "The decision was made for reasons unrelated to the stated problem. "
        "Performance concerns mentioned earlier do not apply to our use case.\n"
    )

    content = adr.raw_content

    # Try to insert contradiction in consequences section
    if sections.consequences or sections.pros or sections.cons:
        target_keywords = ["Consequences", "Impact", "Implications", "Pros", "Cons"]
        # Append contradiction after first matching section
        lines = content.splitlines(keepends=True)
        inserted = False
        keyword_pats = [re.compile(rf"\b{kw}\b", re.IGNORECASE) for kw in target_keywords]
        md_re = re.compile(r"^#{1,6}\s+(.+)$")
        plain_re = re.compile(
            r"^(" + "|".join(target_keywords) + r")\s*:?\s*$", re.IGNORECASE
        )

        result = []
        for line in lines:
            result.append(line)
            stripped = line.strip()
            if not inserted:
                md_m = md_re.match(stripped)
                if md_m and any(p.search(md_m.group(1)) for p in keyword_pats):
                    result.append(contradiction)
                    inserted = True
                elif plain_re.match(stripped):
                    result.append(contradiction)
                    inserted = True

        content = "".join(result)
    else:
        # No consequences section: append contradiction at end
        content += contradiction

    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.ADD_CONTRADICTIONS,
        perturbed_content=content,
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.ADD_CONTRADICTIONS],
        description="Added contradictory statements between context and consequences",
        sections_modified=["consequences"],
    )


def perturb_destroy_structure(adr: ParsedADR) -> PerturbedADR:
    """Remove all headings and flatten content to unstructured prose."""
    lines = adr.raw_content.splitlines()
    result = []

    md_heading_re = re.compile(r"^#{1,6}\s+(.+)$")

    for line in lines:
        stripped = line.strip()
        md_match = md_heading_re.match(stripped)
        if md_match:
            # Convert heading to plain text (remove # markers)
            result.append(md_match.group(1))
        else:
            result.append(line)

    content = "\n".join(result)

    # Also remove any YAML front matter markers
    content = re.sub(r"^---\s*$", "", content, flags=re.MULTILINE)

    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.DESTROY_STRUCTURE,
        perturbed_content=content.strip(),
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.DESTROY_STRUCTURE],
        description="Removed all markdown headings, flattened to unstructured prose",
        sections_modified=["all_headings"],
    )


def perturb_strip_optional(adr: ParsedADR) -> PerturbedADR:
    """Remove all optional sections, keeping only mandatory ones."""
    content = adr.raw_content

    # Remove optional sections: consequences, pros/cons, confirmation, links, sample code
    optional_keywords = [
        ["Consequences", "Impact", "Implications"],
        ["Positive", "Negative"],
        ["Pros", "Cons", "Advantages", "Disadvantages", "Benefits", "Drawbacks"],
        ["Confirmation", "Validation"],
        ["More Information", "References", "Links", "See Also"],
        ["Sample Code", "Code Example", "Example", "Explaination", "Explanation"],
    ]

    for keywords in optional_keywords:
        content = _remove_section_by_heading(content, keywords)

    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.STRIP_ALL_OPTIONAL,
        perturbed_content=content,
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.STRIP_ALL_OPTIONAL],
        description="Removed all optional sections, keeping only context/decision/rationale",
        sections_modified=["consequences", "pros", "cons", "confirmation", "links", "sample_code"],
    )


def perturb_add_drivers(adr: ParsedADR) -> PerturbedADR:
    """Add a Decision Drivers section (positive control: should improve scores)."""
    sections = extract_sections(adr)

    # Generate decision drivers based on context
    drivers_content = (
        "- Need for scalability as user base grows\n"
        "- Developer team familiarity and learning curve\n"
        "- Long-term community support and maintenance\n"
        "- Integration requirements with existing systems\n"
        "- Performance requirements for production workloads"
    )

    content = _insert_after_section(
        adr.raw_content,
        ["Context", "Problem Statement", "Background", "Motivation"],
        "Decision Drivers",
        drivers_content,
    )

    return PerturbedADR(
        original_filename=adr.filename,
        perturbation_type=PerturbationType.ENHANCE_ADD_DRIVERS,
        perturbed_content=content,
        expected_dimension_impacts=_EXPECTED_IMPACTS[PerturbationType.ENHANCE_ADD_DRIVERS],
        description="Added Decision Drivers section (positive control enhancement)",
        sections_modified=["decision_drivers"],
    )


# Registry of all perturbation functions
_PERTURBATION_FUNCTIONS = {
    PerturbationType.REMOVE_CONTEXT: perturb_remove_context,
    PerturbationType.REMOVE_RATIONALE: perturb_remove_rationale,
    PerturbationType.REMOVE_CONSEQUENCES: perturb_remove_consequences,
    PerturbationType.REMOVE_DECISION: perturb_remove_decision,
    PerturbationType.SHALLOW_RATIONALE: perturb_shallow_rationale,
    PerturbationType.VAGUE_DECISION: perturb_vague_decision,
    PerturbationType.ADD_CONTRADICTIONS: perturb_add_contradictions,
    PerturbationType.DESTROY_STRUCTURE: perturb_destroy_structure,
    PerturbationType.STRIP_ALL_OPTIONAL: perturb_strip_optional,
    PerturbationType.ENHANCE_ADD_DRIVERS: perturb_add_drivers,
}


def generate_perturbation(
    adr: ParsedADR,
    perturbation_type: PerturbationType,
) -> PerturbedADR:
    """Generate a single perturbation of an ADR.

    Args:
        adr: The original parsed ADR.
        perturbation_type: Which perturbation to apply.

    Returns:
        PerturbedADR with the perturbed content and expected impacts.
    """
    func = _PERTURBATION_FUNCTIONS[perturbation_type]
    return func(adr)


def generate_all_perturbations(
    adr: ParsedADR,
    types: Optional[list[PerturbationType]] = None,
) -> PerturbationSet:
    """Generate all perturbation variants of a single ADR.

    Args:
        adr: The original parsed ADR.
        types: Specific perturbation types to generate. Defaults to all.

    Returns:
        PerturbationSet with all generated perturbations.
    """
    types = types or list(PerturbationType)

    pset = PerturbationSet(
        original_filename=adr.filename,
        original_content=adr.raw_content,
    )

    for ptype in types:
        try:
            perturbed = generate_perturbation(adr, ptype)
            # Only include if content actually changed
            if perturbed.perturbed_content.strip() != adr.raw_content.strip():
                pset.perturbations.append(perturbed)
        except Exception as e:
            print(f"Warning: Failed to generate {ptype.value} for {adr.filename}: {e}")

    return pset


def select_perturbation_candidates(
    adrs: list[ParsedADR],
    min_sections: int = 2,
    min_word_count: int = 150,
) -> list[ParsedADR]:
    """Select ADRs suitable for perturbation testing.

    Filters to ADRs that have enough content for meaningful perturbation.
    An ADR needs at least context + decision to be a useful perturbation target.

    Args:
        adrs: List of all parsed ADRs.
        min_sections: Minimum mandatory sections present.
        min_word_count: Minimum word count.

    Returns:
        Filtered list of ADRs suitable for perturbation.
    """
    candidates = []
    for adr in adrs:
        sections = extract_sections(adr)
        if (
            sections.mandatory_sections_present >= min_sections
            and adr.word_count >= min_word_count
        ):
            candidates.append(adr)
    return candidates
