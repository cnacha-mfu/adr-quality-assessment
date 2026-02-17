"""
Section Extractor: Stage 2 of the assessment pipeline.

Maps ADR content to MADR sections using regex patterns against standard
and non-standard heading variants. Outputs a structured dictionary per ADR
with section content.

Handles the diversity of section naming observed in the student dataset:
- "Context" / "Context and Problem Statement" / "Problem Statement"
- "Decision" / "Decision Outcome" / "Chosen Option"
- "Rationale" / "Why" / "Justification"
- "Consequences" / "Pros and Cons" / "Impact"
- etc.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from adr_analyser.parsing.parser import ParsedADR


@dataclass
class ExtractedSections:
    """Structured sections extracted from an ADR."""

    # Mandatory MADR sections
    context: Optional[str] = None
    decision: Optional[str] = None
    decision_outcome: Optional[str] = None

    # Important content sections
    decision_drivers: Optional[str] = None
    considered_options: Optional[str] = None
    rationale: Optional[str] = None

    # Consequences
    consequences: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None

    # Optional sections
    confirmation: Optional[str] = None
    more_information: Optional[str] = None
    links: Optional[str] = None

    # Metadata sections (extracted separately from body)
    status: Optional[str] = None
    date: Optional[str] = None
    deciders: Optional[str] = None

    # Non-standard sections (captured for completeness)
    issue: Optional[str] = None
    solution: Optional[str] = None
    sample_code: Optional[str] = None

    # Raw section map for dimensions not covered above
    other_sections: dict[str, str] = field(default_factory=dict)

    @property
    def mandatory_sections_present(self) -> int:
        """Count of mandatory sections that are present and non-empty."""
        count = 0
        if self.context:
            count += 1
        if self.decision or self.decision_outcome:
            count += 1
        if self.rationale:
            count += 1
        return count

    @property
    def optional_sections_present(self) -> int:
        """Count of optional sections that are present and non-empty."""
        count = 0
        if self.decision_drivers:
            count += 1
        if self.considered_options:
            count += 1
        if self.consequences or (self.pros and self.cons):
            count += 1
        if self.confirmation:
            count += 1
        if self.more_information or self.links:
            count += 1
        return count

    @property
    def total_sections_present(self) -> int:
        """Total count of all recognized sections present."""
        return self.mandatory_sections_present + self.optional_sections_present

    def to_dict(self) -> dict[str, Optional[str]]:
        """Convert to dictionary for serialization."""
        return {
            "context": self.context,
            "decision": self.decision,
            "decision_outcome": self.decision_outcome,
            "decision_drivers": self.decision_drivers,
            "considered_options": self.considered_options,
            "rationale": self.rationale,
            "consequences": self.consequences,
            "pros": self.pros,
            "cons": self.cons,
            "confirmation": self.confirmation,
            "more_information": self.more_information,
            "links": self.links,
            "status": self.status,
            "date": self.date,
            "deciders": self.deciders,
            "issue": self.issue,
            "solution": self.solution,
            "sample_code": self.sample_code,
        }


# Section heading patterns: maps canonical name → list of regex patterns
# Patterns are matched case-insensitively against H2/H3 headings
_SECTION_PATTERNS: dict[str, list[str]] = {
    "context": [
        r"context(?:\s+and\s+problem\s+statement)?",
        r"problem\s+statement",
        r"background",
        r"motivation",
        r"context",
    ],
    "decision": [
        r"decision(?!\s+driver)(?!\s+outcome)",
        r"chosen\s+option",
        r"selected\s+option",
    ],
    "decision_outcome": [
        r"decision\s+outcome",
        r"outcome",
    ],
    "decision_drivers": [
        r"decision\s+drivers?",
        r"drivers?",
        r"forces",
        r"requirements",
        r"constraints",
    ],
    "considered_options": [
        r"considered\s+options?",
        r"options?\s+considered",
        r"alternatives?",
        r"options?",
    ],
    "rationale": [
        r"rationale",
        r"justification",
        r"reasoning",
        r"why",
        r"argument",
    ],
    "consequences": [
        r"consequences?",
        r"impact",
        r"implications?",
        r"pros?\s+(?:and|&)\s+cons?",
    ],
    "pros": [
        r"pros?(?:\s*:)?",
        r"advantages?",
        r"benefits?",
        r"positive(?:\s+consequences)?",
        r"good",
    ],
    "cons": [
        r"cons?(?:\s*:)?",
        r"disadvantages?",
        r"drawbacks?",
        r"negative(?:\s+consequences)?",
        r"risks?",
        r"bad",
    ],
    "confirmation": [
        r"confirmation",
        r"validation",
        r"verification",
    ],
    "more_information": [
        r"more\s+information",
        r"additional\s+information",
        r"references?",
        r"links?",
        r"further\s+reading",
        r"see\s+also",
        r"related",
    ],
    "status": [
        r"status",
    ],
    "date": [
        r"date",
        r"created",
    ],
    "deciders": [
        r"deciders?",
        r"authors?",
        r"participants?",
    ],
    "issue": [
        r"issue",
        r"problem",
    ],
    "solution": [
        r"solution",
        r"approach",
    ],
    "sample_code": [
        r"sample\s+code",
        r"code\s+example",
        r"example\s+code",
        r"code",
        r"implementation\s+example",
        r"explaination",  # typo seen in dataset
        r"explanation",
    ],
}

# Compile patterns
_COMPILED_PATTERNS: dict[str, list[re.Pattern]] = {
    name: [re.compile(p, re.IGNORECASE) for p in patterns]
    for name, patterns in _SECTION_PATTERNS.items()
}


def _match_section_name(heading_text: str) -> Optional[str]:
    """Match a heading text to a canonical section name."""
    # Clean the heading text
    cleaned = heading_text.strip().rstrip(":").strip()

    for section_name, patterns in _COMPILED_PATTERNS.items():
        for pattern in patterns:
            if pattern.fullmatch(cleaned):
                return section_name
    return None


def _split_into_sections(body: str) -> list[tuple[int, str, str]]:
    """Split the markdown body into (heading_level, heading_text, content) tuples.

    Returns a list of tuples where each tuple represents a section with:
    - heading level (1-6)
    - heading text
    - content following the heading until the next heading of same or higher level

    Handles two formats:
    1. Standard markdown headings (# Heading)
    2. Plain-text headings (standalone lines matching known section names),
       common in ADRs exported from Google Docs or PDFs.
    """
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(body))

    if matches:
        # Standard markdown heading mode
        sections = []
        for i, match in enumerate(matches):
            level = len(match.group(1))
            heading = match.group(2).strip()
            start = match.end()

            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(body)

            content = body[start:end].strip()
            sections.append((level, heading, content))

        return sections

    # Fallback: plain-text heading detection for ADRs without markdown formatting.
    # These are typically exported from Google Docs/PDF where # markers are lost.
    return _split_plain_text_sections(body)


# Known section name patterns for plain-text heading detection
_PLAIN_TEXT_HEADING_PATTERNS = [
    re.compile(
        r"^(Context(?:\s+and\s+Problem\s+Statement)?|Problem\s+Statement|Background|"
        r"Motivation|Decision(?:\s+Outcome|\s+Drivers?)?|Chosen\s+Option|"
        r"Considered\s+Options?|Alternatives?|Options?|"
        r"Rationale|Justification|Reasoning|Why|"
        r"Consequences?|Pros?\s+(?:and|&)\s+Cons?|Impact|"
        r"Confirmation|More\s+Information|References?|Links?|"
        r"Status|Date|Deciders?|Title|"
        r"Issue|Problem|Solution|Approach|"
        r"Sample\s+Code|Code\s+Example|Positive|Negative|"
        r"Pros?|Cons?|Advantages?|Disadvantages?|Benefits?|Drawbacks?)\s*:?\s*$",
        re.IGNORECASE,
    ),
]


def _split_plain_text_sections(body: str) -> list[tuple[int, str, str]]:
    """Split body using plain-text headings (lines matching known section names).

    Detects lines that consist solely of a known section keyword (with optional
    trailing colon/whitespace) and treats them as section boundaries.
    """
    lines = body.splitlines()
    sections = []
    current_heading = ""
    current_content_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_content_lines.append("")
            continue

        # Check if this line is a plain-text heading
        is_heading = False
        for pattern in _PLAIN_TEXT_HEADING_PATTERNS:
            if pattern.match(stripped):
                is_heading = True
                break

        if is_heading:
            # Save previous section if any
            if current_heading or any(l.strip() for l in current_content_lines):
                content = "\n".join(current_content_lines).strip()
                sections.append((2, current_heading, content))

            current_heading = stripped.rstrip(":").strip()
            current_content_lines = []
        else:
            current_content_lines.append(line)

    # Save last section
    if current_heading or any(l.strip() for l in current_content_lines):
        content = "\n".join(current_content_lines).strip()
        sections.append((2, current_heading, content))

    return sections


def extract_sections(adr: ParsedADR) -> ExtractedSections:
    """Extract and map sections from a parsed ADR.

    Args:
        adr: A ParsedADR object from the parser.

    Returns:
        ExtractedSections with mapped section content.
    """
    result = ExtractedSections()

    # Set metadata from parser
    if adr.metadata.status:
        result.status = adr.metadata.status
    if adr.metadata.date:
        result.date = str(adr.metadata.date)
    if adr.metadata.deciders:
        result.deciders = adr.metadata.deciders

    # Split body into sections
    raw_sections = _split_into_sections(adr.body)

    # Metadata fields that should not be overridden by section extraction
    _METADATA_FIELDS = {"status", "date", "deciders"}

    # Map each section to its canonical name
    for level, heading, content in raw_sections:
        if not heading and not content.strip():
            continue

        canonical = _match_section_name(heading)

        if canonical and content.strip():
            # Skip metadata fields already set from the parser
            if canonical in _METADATA_FIELDS and getattr(result, canonical, None) is not None:
                continue

            # Set the appropriate field
            current_value = getattr(result, canonical, None)
            if current_value is None:
                setattr(result, canonical, content)
            else:
                # Append to existing content (e.g., multiple sub-sections)
                setattr(result, canonical, current_value + "\n\n" + content)
        elif heading and content.strip():
            # Store unrecognized sections
            result.other_sections[heading] = content

    # Post-processing: if consequences has pros/cons subsections, extract them
    if result.consequences and not result.pros:
        _extract_pros_cons_from_consequences(result)

    # If no rationale but decision has "because" clause, extract it
    if not result.rationale and result.decision:
        _extract_rationale_from_decision(result)

    return result


def _extract_pros_cons_from_consequences(sections: ExtractedSections) -> None:
    """Try to extract pros and cons from the consequences section."""
    text = sections.consequences or ""

    # Look for ### Pros / ### Cons subsections
    pros_pattern = re.compile(
        r"###?\s*(?:Pros?|Advantages?|Benefits?|Positive).*?\n(.*?)(?=###?\s*(?:Cons?|Disadvantages?|Drawbacks?|Negative|Risks?)|$)",
        re.IGNORECASE | re.DOTALL,
    )
    cons_pattern = re.compile(
        r"###?\s*(?:Cons?|Disadvantages?|Drawbacks?|Negative|Risks?).*?\n(.*?)(?=###?\s|$)",
        re.IGNORECASE | re.DOTALL,
    )

    m = pros_pattern.search(text)
    if m:
        sections.pros = m.group(1).strip()
    m = cons_pattern.search(text)
    if m:
        sections.cons = m.group(1).strip()


def _extract_rationale_from_decision(sections: ExtractedSections) -> None:
    """Extract rationale from decision text if it contains a because-clause."""
    text = sections.decision or ""
    because_pattern = re.compile(r"\bbecause\b(.+)", re.IGNORECASE | re.DOTALL)
    m = because_pattern.search(text)
    if m:
        sections.rationale = m.group(1).strip()
