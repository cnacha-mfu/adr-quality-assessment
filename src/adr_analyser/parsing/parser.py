"""
ADR Parser: Stage 1 of the assessment pipeline.

Parses ADR markdown files, extracting:
- YAML front matter (status, date, deciders)
- Markdown body text
- Basic structural metadata (word count, heading count, etc.)

Handles the diversity of ADR formats observed in the student dataset,
including non-standard formatting and loose MADR adherence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ADRMetadata:
    """Metadata extracted from YAML front matter or inline fields."""

    status: Optional[str] = None
    date: Optional[str] = None
    deciders: Optional[str] = None
    title: Optional[str] = None
    adr_id: Optional[str] = None
    raw_frontmatter: dict = field(default_factory=dict)


@dataclass
class ParsedADR:
    """A fully parsed ADR document."""

    file_path: str
    filename: str
    cohort: str  # e.g., "2024" or "2025"
    raw_content: str
    metadata: ADRMetadata
    body: str  # Markdown body without front matter
    title: str
    word_count: int
    heading_count: int
    has_code_block: bool
    headings: list[tuple[int, str]]  # (level, text) pairs


# YAML front matter pattern: --- at start, content, ---
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Title pattern: first H1 heading
_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

# ADR ID pattern in title: ADR-NNN or ADR NNN
_ADR_ID_RE = re.compile(r"ADR[-\s]?(\d+)", re.IGNORECASE)

# All headings
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

# Code blocks
_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```")

# Inline metadata patterns (for ADRs without front matter)
_STATUS_RE = re.compile(r"##?\s*Status\s*\n+\s*(.+?)(?:\n|$)", re.IGNORECASE)
_DATE_RE = re.compile(r"##?\s*Date\s*\n+\s*(.+?)(?:\n|$)", re.IGNORECASE)
_DECIDERS_RE = re.compile(r"##?\s*Deciders?\s*\n+\s*(.+?)(?:\n|$)", re.IGNORECASE)


def _extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML front matter and return (metadata_dict, remaining_body)."""
    match = _FRONTMATTER_RE.match(content)
    if match:
        try:
            fm = yaml.safe_load(match.group(1)) or {}
            body = content[match.end():]
            return fm, body
        except yaml.YAMLError:
            return {}, content
    return {}, content


def _extract_inline_metadata(body: str) -> dict:
    """Extract metadata from inline Status/Date/Deciders sections."""
    meta = {}
    m = _STATUS_RE.search(body)
    if m:
        meta["status"] = m.group(1).strip()
    m = _DATE_RE.search(body)
    if m:
        meta["date"] = m.group(1).strip()
    m = _DECIDERS_RE.search(body)
    if m:
        meta["deciders"] = m.group(1).strip()
    return meta


def _extract_title(body: str) -> str:
    """Extract the title from the first H1 heading, or first line."""
    m = _TITLE_RE.search(body)
    if m:
        return m.group(1).strip()
    # Fallback: first non-empty line
    for line in body.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return "Untitled"


def _extract_headings(body: str) -> list[tuple[int, str]]:
    """Extract all headings with their levels."""
    return [(len(m.group(1)), m.group(2).strip()) for m in _HEADING_RE.finditer(body)]


def _count_words(text: str) -> int:
    """Count words in text, excluding code blocks."""
    # Remove code blocks before counting
    cleaned = _CODE_BLOCK_RE.sub("", text)
    return len(cleaned.split())


def parse_adr(file_path: str | Path) -> ParsedADR:
    """Parse a single ADR markdown file.

    Args:
        file_path: Path to the ADR markdown file.

    Returns:
        ParsedADR with all extracted components.
    """
    file_path = Path(file_path)
    content = file_path.read_text(encoding="utf-8", errors="replace")

    # Determine cohort from path
    cohort = "unknown"
    parts = file_path.parts
    for part in parts:
        if part in ("2024", "2025", "2023", "2026"):
            cohort = part
            break

    # Extract front matter
    frontmatter, body = _extract_frontmatter(content)

    # Build metadata
    inline_meta = _extract_inline_metadata(body)
    metadata = ADRMetadata(
        status=frontmatter.get("status") or inline_meta.get("status"),
        date=frontmatter.get("date") or inline_meta.get("date"),
        deciders=frontmatter.get("deciders") or inline_meta.get("deciders"),
        raw_frontmatter=frontmatter,
    )

    # Extract title
    title = _extract_title(body)
    metadata.title = title

    # Check for ADR ID in title
    id_match = _ADR_ID_RE.search(title)
    if id_match:
        metadata.adr_id = f"ADR-{id_match.group(1)}"

    # Extract headings
    headings = _extract_headings(body)

    return ParsedADR(
        file_path=str(file_path),
        filename=file_path.name,
        cohort=cohort,
        raw_content=content,
        metadata=metadata,
        body=body,
        title=title,
        word_count=_count_words(body),
        heading_count=len(headings),
        has_code_block=bool(_CODE_BLOCK_RE.search(body)),
        headings=headings,
    )


def parse_adr_directory(directory: str | Path) -> list[ParsedADR]:
    """Parse all ADR markdown files in a directory tree.

    Args:
        directory: Root directory to scan for *.md files.

    Returns:
        List of ParsedADR objects, sorted by file path.
    """
    directory = Path(directory)
    adrs = []
    for md_file in sorted(directory.rglob("*.md")):
        # Skip plan.md and other non-ADR files
        if md_file.name.lower() in ("plan.md", "readme.md", "changelog.md"):
            continue
        try:
            adr = parse_adr(md_file)
            adrs.append(adr)
        except Exception as e:
            print(f"Warning: Failed to parse {md_file}: {e}")
    return adrs
