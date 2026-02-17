"""
ADR Quality Model: 10-dimension hierarchical quality model.

Based on:
- MADR 4.0.0 template structure (Kopp, Armbruster & Zimmermann, 2018)
- Zimmermann's ADR Author Pledge (2023) — 7 principles + 11 anti-patterns
- ISO/IEC/IEEE 42010:2022 (architecture description quality)
- IEEE 830 requirements quality characteristics
- QOC framework (MacLean et al.) and IBIS (Kunz & Rittel)
- Siebert et al. (2022) quality model construction methodology

The model is organized into three categories:
  A. Structural Quality (completeness, conformance)
  B. Content Quality (context, alternatives, rationale, consequences, decision)
  C. Documentation Quality (clarity, consistency, traceability)

Each dimension uses a 4-point anchored Likert scale (no neutral midpoint)
to force discrimination and avoid central tendency bias.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class QualityCategory(str, Enum):
    """Top-level quality category."""

    STRUCTURAL = "structural"
    CONTENT = "content"
    DOCUMENTATION = "documentation"


@dataclass(frozen=True)
class ScaleAnchor:
    """A single anchor point on the 4-point scoring scale."""

    score: int  # 1–4
    label: str
    description: str


@dataclass(frozen=True)
class GQMEntry:
    """Goal-Question-Metric entry for operationalizing a dimension (Basili & Weiss, 1984)."""

    goal: str
    questions: list[str]
    metrics: list[str]


@dataclass(frozen=True)
class QualityDimension:
    """A single quality dimension with its definition, GQM, and scale anchors."""

    id: str  # e.g. "A1", "B3"
    name: str
    category: QualityCategory
    definition: str
    gqm: GQMEntry
    anchors: list[ScaleAnchor]
    weight: float = 1.0  # default equal weight; adjusted after Delphi validation
    literature_sources: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Dimension definitions
# ---------------------------------------------------------------------------

A1_COMPLETENESS = QualityDimension(
    id="A1",
    name="Completeness",
    category=QualityCategory.STRUCTURAL,
    definition=(
        "All relevant MADR sections are present and filled with substantive content. "
        "Mandatory sections include Context/Problem Statement, Considered Options (or Decision), "
        "and Decision Outcome. Optional but expected sections include Decision Drivers, "
        "Pros/Cons of each option, Consequences, and Confirmation."
    ),
    gqm=GQMEntry(
        goal="Assess whether the ADR contains all sections necessary for a complete record.",
        questions=[
            "Is a context or problem statement present and non-trivial?",
            "Are at least two options explicitly listed or one decision clearly stated?",
            "Is a decision outcome section present?",
            "Are consequences (pros and cons) documented?",
            "Are optional sections (drivers, confirmation, links) present where relevant?",
        ],
        metrics=[
            "Count of mandatory sections present (0–3)",
            "Count of optional sections present (0–5)",
            "Proportion of sections with substantive content (>1 sentence)",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "Severely incomplete",
            "Missing two or more mandatory sections (e.g., no context, no decision, "
            "or no rationale). The record cannot function as a decision record.",
        ),
        ScaleAnchor(
            2,
            "Partially complete",
            "All mandatory sections present but at least two are trivially short "
            "(one sentence or a placeholder). Optional sections largely absent.",
        ),
        ScaleAnchor(
            3,
            "Substantially complete",
            "All mandatory sections present with substantive content. "
            "At least two optional sections (e.g., decision drivers, consequences) are included.",
        ),
        ScaleAnchor(
            4,
            "Fully complete",
            "All mandatory and relevant optional sections present with substantive, "
            "detailed content. Nothing material is missing for understanding the decision.",
        ),
    ],
    literature_sources=[
        "MADR 4.0.0 (Kopp et al., 2018)",
        "Zimmermann ADR Author Pledge (2023)",
    ],
)

A2_STRUCTURAL_CONFORMANCE = QualityDimension(
    id="A2",
    name="Structural Conformance",
    category=QualityCategory.STRUCTURAL,
    definition=(
        "Adherence to a recognized ADR template format. Correct use of headings, "
        "consistent section ordering, presence of metadata (status, date, deciders), "
        "and appropriate use of markdown formatting."
    ),
    gqm=GQMEntry(
        goal="Assess whether the ADR follows a recognizable template structure.",
        questions=[
            "Does the ADR use a consistent heading hierarchy (e.g., H1 title, H2 sections)?",
            "Is the section order logical and consistent with MADR conventions?",
            "Is metadata (status, date, author/deciders) present?",
            "Is markdown formatting used correctly (lists, code blocks, links)?",
        ],
        metrics=[
            "Number of recognized MADR headings used correctly",
            "Presence of metadata fields (binary per field)",
            "Heading hierarchy consistency (no skipped levels)",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "No recognizable structure",
            "Free-form text with no headings or sections. Cannot be mapped to any "
            "ADR template. May be a single paragraph or bullet list.",
        ),
        ScaleAnchor(
            2,
            "Minimal structure",
            "Some headings present but inconsistent hierarchy, missing key section "
            "labels, or sections in non-standard order. No metadata.",
        ),
        ScaleAnchor(
            3,
            "Good structure",
            "Follows a recognizable template (MADR or similar) with consistent headings. "
            "Minor issues such as missing metadata or slight ordering deviations.",
        ),
        ScaleAnchor(
            4,
            "Exemplary structure",
            "Strict adherence to MADR template with correct heading hierarchy, all "
            "metadata fields, logical section ordering, and proper markdown formatting.",
        ),
    ],
    literature_sources=[
        "MADR 4.0.0 (Kopp et al., 2018)",
        "ISO/IEC/IEEE 42010:2022",
    ],
)

B1_CONTEXT_ADEQUACY = QualityDimension(
    id="B1",
    name="Context Adequacy",
    category=QualityCategory.CONTENT,
    definition=(
        "Clarity and sufficiency of the problem statement, including the architectural "
        "significance of the decision, the forces and constraints at play, and the "
        "decision drivers that motivate the need for a decision."
    ),
    gqm=GQMEntry(
        goal="Assess whether the context provides enough information to understand why "
        "a decision is needed.",
        questions=[
            "Is the problem or need clearly stated?",
            "Is the architectural significance of the decision explained?",
            "Are the forces, constraints, or drivers that shape the decision identified?",
            "Is there enough context for a reader unfamiliar with the project to understand "
            "the situation?",
        ],
        metrics=[
            "Presence of explicit problem statement (binary)",
            "Number of decision drivers or forces identified",
            "Specificity of context (project-specific vs. generic)",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "Missing or trivial context",
            "No context section, or context is a single vague sentence "
            "(e.g., 'We need a database'). No drivers or constraints mentioned.",
        ),
        ScaleAnchor(
            2,
            "Generic context",
            "Problem is stated but in generic terms without project-specific details. "
            "Decision drivers are implicit or absent. A reader cannot understand the "
            "specific situation motivating the decision.",
        ),
        ScaleAnchor(
            3,
            "Adequate context",
            "Problem is clearly stated with project-specific details. At least two "
            "decision drivers or constraints are explicitly identified. A reader can "
            "understand why a decision is needed.",
        ),
        ScaleAnchor(
            4,
            "Rich context",
            "Thorough problem description with architectural significance explained. "
            "Multiple drivers and constraints identified and prioritized. Background "
            "assumptions stated. A new team member could fully understand the situation.",
        ),
    ],
    literature_sources=[
        "Zimmermann ADR Author Pledge (2023) — 'present explicitly'",
        "ISO/IEC/IEEE 42010:2022 — architecture concerns",
        "QOC framework (MacLean et al., 1991)",
    ],
)

B2_ALTERNATIVES_COVERAGE = QualityDimension(
    id="B2",
    name="Alternatives Coverage",
    category=QualityCategory.CONTENT,
    definition=(
        "The number, diversity, and feasibility of options considered before making "
        "the decision. Zimmermann's guidelines require at least two alternatives. "
        "Each alternative should be described sufficiently for evaluation."
    ),
    gqm=GQMEntry(
        goal="Assess whether the ADR demonstrates adequate consideration of alternatives.",
        questions=[
            "Are at least two distinct alternatives explicitly listed?",
            "Is each alternative described with enough detail to evaluate it?",
            "Are the alternatives genuinely different (not trivial variants)?",
            "Are clearly infeasible or strawman options avoided?",
        ],
        metrics=[
            "Number of alternatives listed",
            "Average description length per alternative (words)",
            "Diversity of alternatives (subjective assessment)",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "No alternatives",
            "Only one option presented (the chosen one) with no alternatives discussed. "
            "Violates Zimmermann's minimum requirement of considering ≥2 options.",
        ),
        ScaleAnchor(
            2,
            "Superficial alternatives",
            "Two or more alternatives listed but described in a single sentence each, "
            "or alternatives are trivially similar or obvious strawmen.",
        ),
        ScaleAnchor(
            3,
            "Adequate alternatives",
            "Two or more genuinely distinct alternatives with sufficient description "
            "to understand each option's approach. Some evaluation criteria applied.",
        ),
        ScaleAnchor(
            4,
            "Thorough alternatives analysis",
            "Three or more well-described alternatives with clear differentiation. "
            "Each option evaluated against the stated decision drivers. "
            "Rejected options have documented reasons for rejection.",
        ),
    ],
    literature_sources=[
        "Zimmermann (2023) — ≥2 options requirement",
        "IBIS (Kunz & Rittel, 1970) — issue-position-argument",
    ],
)

B3_RATIONALE_DEPTH = QualityDimension(
    id="B3",
    name="Rationale Depth",
    category=QualityCategory.CONTENT,
    definition=(
        "Quality of the justification for the chosen decision. Includes explicit "
        "because-clauses linking the decision to drivers, acknowledgment of tradeoffs, "
        "and evidence or reasoning supporting the choice over alternatives."
    ),
    gqm=GQMEntry(
        goal="Assess the quality and depth of the justification for the decision outcome.",
        questions=[
            "Is there an explicit because-clause or rationale statement?",
            "Does the rationale reference the stated decision drivers?",
            "Are tradeoffs between alternatives acknowledged?",
            "Is evidence (benchmarks, references, experience) provided?",
        ],
        metrics=[
            "Presence of explicit because-clause (binary)",
            "Number of drivers referenced in rationale",
            "Tradeoff acknowledgment (binary)",
            "Evidence types cited (count)",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "No rationale",
            "No rationale provided, or only an assertion without reasoning "
            "(e.g., 'We chose X because it is the best'). Decision appears arbitrary.",
        ),
        ScaleAnchor(
            2,
            "Shallow rationale",
            "Generic rationale without reference to project context or decision drivers. "
            "Reasons are vague (e.g., 'It is popular and well-supported'). "
            "No tradeoff discussion.",
        ),
        ScaleAnchor(
            3,
            "Adequate rationale",
            "Rationale references specific decision drivers and acknowledges at least "
            "one tradeoff. The reader understands why this option was chosen over "
            "alternatives, though depth could be improved.",
        ),
        ScaleAnchor(
            4,
            "Exemplary rationale",
            "Deep rationale with explicit tradeoff analysis linking each driver to the "
            "chosen option's strengths/weaknesses. Evidence or experience cited. "
            "Clear explanation of why alternatives were rejected.",
        ),
    ],
    literature_sources=[
        "Zimmermann (2023) — 'be honest and candid'",
        "Design rationale literature (QOC, IBIS, DRL)",
        "IEEE 830 — justification characteristics",
    ],
)

B4_CONSEQUENCE_SPECIFICITY = QualityDimension(
    id="B4",
    name="Consequence Specificity",
    category=QualityCategory.CONTENT,
    definition=(
        "Concrete articulation of both positive and negative consequences of the "
        "decision. Consequences should be specific, measurable where possible, and "
        "cover technical, organizational, and process impacts."
    ),
    gqm=GQMEntry(
        goal="Assess whether consequences are specific and cover both positive and "
        "negative impacts.",
        questions=[
            "Are positive consequences (pros/benefits) explicitly listed?",
            "Are negative consequences (cons/risks/costs) explicitly listed?",
            "Are consequences specific to the project rather than generic?",
            "Are consequences actionable (can be verified or monitored)?",
        ],
        metrics=[
            "Number of positive consequences listed",
            "Number of negative consequences listed",
            "Specificity rating (generic vs. project-specific)",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "No consequences",
            "No consequences section, or consequences are completely absent. "
            "The reader has no understanding of the decision's impact.",
        ),
        ScaleAnchor(
            2,
            "Vague consequences",
            "Consequences listed but generic and applicable to any technology choice "
            "(e.g., 'Better performance' or 'Learning curve'). Only pros or only cons, "
            "not both.",
        ),
        ScaleAnchor(
            3,
            "Adequate consequences",
            "Both pros and cons listed with some project-specific detail. "
            "At least two concrete consequences that relate to the actual decision context.",
        ),
        ScaleAnchor(
            4,
            "Detailed consequences",
            "Comprehensive, project-specific consequences covering technical, process, "
            "and team impacts. Both positive and negative clearly articulated. "
            "Mitigation strategies for risks may be mentioned.",
        ),
    ],
    literature_sources=[
        "MADR 4.0.0 — Consequences section",
        "ISO/IEC/IEEE 42010:2022 — decision consequences",
    ],
)

B5_DECISION_SPECIFICITY = QualityDimension(
    id="B5",
    name="Decision Specificity",
    category=QualityCategory.CONTENT,
    definition=(
        "How concrete, actionable, and unambiguous the chosen option is stated. "
        "The decision should clearly identify what was decided, leaving no room "
        "for misinterpretation about the action to be taken."
    ),
    gqm=GQMEntry(
        goal="Assess whether the decision outcome is stated concretely and unambiguously.",
        questions=[
            "Is the chosen option clearly and explicitly stated?",
            "Is the decision specific enough to act upon?",
            "Is the scope of the decision clear (what it applies to and what it does not)?",
            "Is the decision status indicated (proposed, accepted, deprecated)?",
        ],
        metrics=[
            "Clarity of decision statement (subjective 1-4)",
            "Presence of decision status (binary)",
            "Actionability (can a developer implement based on this?)",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "Unclear decision",
            "No clear decision statement, or the decision is buried in prose and "
            "ambiguous. A reader cannot determine what was actually decided.",
        ),
        ScaleAnchor(
            2,
            "Vague decision",
            "Decision is stated but vaguely (e.g., 'We will use a modern framework'). "
            "Lacks specificity about the exact choice and its scope.",
        ),
        ScaleAnchor(
            3,
            "Clear decision",
            "Decision is clearly stated with the specific option identified. "
            "Scope is mostly clear, though some implementation details may be missing.",
        ),
        ScaleAnchor(
            4,
            "Precise decision",
            "Decision is precisely and unambiguously stated with specific technology, "
            "version, and scope. Status is indicated. A developer could act on this "
            "decision without seeking clarification.",
        ),
    ],
    literature_sources=[
        "Zimmermann (2023) — Y-statement template",
        "IEEE 830 — unambiguity requirement",
    ],
)

C1_CLARITY_READABILITY = QualityDimension(
    id="C1",
    name="Clarity and Readability",
    category=QualityCategory.DOCUMENTATION,
    definition=(
        "Language quality, logical flow, and editorial polish of the document. "
        "The ADR should be readable by its intended audience (development team, "
        "future maintainers) without requiring excessive interpretation."
    ),
    gqm=GQMEntry(
        goal="Assess the linguistic and structural clarity of the ADR document.",
        questions=[
            "Is the language clear and free of major grammatical errors?",
            "Does the document flow logically from context to decision to consequences?",
            "Is technical jargon used appropriately and consistently?",
            "Is the document appropriately concise (not excessively verbose or terse)?",
        ],
        metrics=[
            "Readability assessment (subjective 1-4)",
            "Logical flow assessment (subjective 1-4)",
            "Appropriate length (neither excessively short nor padded)",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "Poor readability",
            "Numerous grammatical errors, unclear sentences, or incoherent structure. "
            "Significant effort required to understand the content. May appear "
            "machine-translated or hastily written.",
        ),
        ScaleAnchor(
            2,
            "Below-average readability",
            "Understandable but with noticeable language issues, awkward phrasing, "
            "or disjointed flow between sections. Some sentences require re-reading.",
        ),
        ScaleAnchor(
            3,
            "Good readability",
            "Clear, professional language with logical flow. Minor issues do not "
            "impede understanding. Appropriate use of technical terminology.",
        ),
        ScaleAnchor(
            4,
            "Excellent readability",
            "Well-written, concise, and polished. Logical progression from problem "
            "to decision to consequences. Could serve as an exemplar document.",
        ),
    ],
    literature_sources=[
        "Zimmermann (2023) — 'invest in documentation quality'",
        "IEEE 830 — readability characteristics",
    ],
)

C2_CONSISTENCY = QualityDimension(
    id="C2",
    name="Consistency",
    category=QualityCategory.DOCUMENTATION,
    definition=(
        "Absence of internal contradictions, uniform terminology throughout the "
        "document, and alignment between stated drivers/criteria and the actual "
        "evaluation of alternatives."
    ),
    gqm=GQMEntry(
        goal="Assess internal consistency of the ADR document.",
        questions=[
            "Are there any contradictions between sections?",
            "Is terminology used consistently throughout?",
            "Do the evaluation criteria align with the stated decision drivers?",
            "Does the decision outcome logically follow from the analysis?",
        ],
        metrics=[
            "Number of internal contradictions identified",
            "Terminology consistency (subjective 1-4)",
            "Driver-to-evaluation alignment (subjective 1-4)",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "Significant contradictions",
            "Clear contradictions between sections (e.g., context says performance is "
            "critical but evaluation ignores it). Terminology shifts meaning. "
            "Decision does not follow from the stated analysis.",
        ),
        ScaleAnchor(
            2,
            "Minor inconsistencies",
            "No major contradictions but some misalignment between drivers and evaluation, "
            "or inconsistent use of terms. The reader may notice gaps in logic.",
        ),
        ScaleAnchor(
            3,
            "Mostly consistent",
            "Consistent terminology and logical alignment between sections. "
            "Decision follows from the analysis. Minor terminology variations "
            "do not cause confusion.",
        ),
        ScaleAnchor(
            4,
            "Fully consistent",
            "Perfect internal consistency. Decision drivers are explicitly referenced "
            "in evaluation. Terminology is uniform. The document reads as a coherent "
            "whole with no logical gaps.",
        ),
    ],
    literature_sources=[
        "IEEE 830 — consistency requirement",
        "ISO/IEC/IEEE 42010:2022 — consistency across views",
    ],
)

C3_TRACEABILITY = QualityDimension(
    id="C3",
    name="Traceability",
    category=QualityCategory.DOCUMENTATION,
    definition=(
        "Explicit links to requirements, related ADRs, external references, "
        "and other artifacts that provide context for or are affected by this decision."
    ),
    gqm=GQMEntry(
        goal="Assess whether the ADR establishes traceable links to related artifacts.",
        questions=[
            "Are related requirements or user stories referenced?",
            "Are related or superseded ADRs linked?",
            "Are external references (documentation, articles, benchmarks) cited?",
            "Is the scope of impact (affected components/services) identified?",
        ],
        metrics=[
            "Number of internal links (to ADRs, requirements)",
            "Number of external references",
            "Presence of supersedes/superseded-by relationships",
        ],
    ),
    anchors=[
        ScaleAnchor(
            1,
            "No traceability",
            "No references to any external or internal artifacts. The ADR exists "
            "in complete isolation with no links to the broader project context.",
        ),
        ScaleAnchor(
            2,
            "Minimal traceability",
            "One or two generic references (e.g., a link to official documentation) "
            "but no links to project requirements, related ADRs, or specific evidence.",
        ),
        ScaleAnchor(
            3,
            "Adequate traceability",
            "References to relevant external documentation and at least one internal "
            "link (related ADR, requirement, or component). Reader can find "
            "supporting information.",
        ),
        ScaleAnchor(
            4,
            "Comprehensive traceability",
            "Rich network of links: related ADRs, requirements/user stories, external "
            "documentation, benchmarks, and identification of affected components. "
            "Supports full decision archaeology.",
        ),
    ],
    literature_sources=[
        "MADR 4.0.0 — More Information / Links section",
        "IEEE 830 — traceability requirement",
        "ISO/IEC/IEEE 42010:2022 — architecture description correspondence",
    ],
)

# ---------------------------------------------------------------------------
# Quality model registry
# ---------------------------------------------------------------------------

QUALITY_MODEL: dict[str, QualityDimension] = {
    "A1": A1_COMPLETENESS,
    "A2": A2_STRUCTURAL_CONFORMANCE,
    "B1": B1_CONTEXT_ADEQUACY,
    "B2": B2_ALTERNATIVES_COVERAGE,
    "B3": B3_RATIONALE_DEPTH,
    "B4": B4_CONSEQUENCE_SPECIFICITY,
    "B5": B5_DECISION_SPECIFICITY,
    "C1": C1_CLARITY_READABILITY,
    "C2": C2_CONSISTENCY,
    "C3": C3_TRACEABILITY,
}

# Ordered list of all dimension IDs
DIMENSION_ORDER = ["A1", "A2", "B1", "B2", "B3", "B4", "B5", "C1", "C2", "C3"]


def get_dimension(dim_id: str) -> QualityDimension:
    """Get a quality dimension by its ID (e.g., 'A1', 'B3')."""
    if dim_id not in QUALITY_MODEL:
        raise KeyError(f"Unknown dimension ID: {dim_id}. Valid IDs: {list(QUALITY_MODEL.keys())}")
    return QUALITY_MODEL[dim_id]


def get_dimensions_by_category(category: QualityCategory) -> list[QualityDimension]:
    """Get all dimensions belonging to a category."""
    return [d for d in QUALITY_MODEL.values() if d.category == category]
