"""
Feedback Generator: Stage 5 of the assessment pipeline.

Takes all dimension scores with reasoning as input and generates:
1. A 2-3 sentence overall assessment
2. Top 3 strengths
3. Top 3 specific improvement suggestions with rubric references
4. (Optional) A suggested revision for the weakest section

Two modes:
- Template-based: deterministic feedback from scores (no LLM needed)
- LLM-enhanced: uses an LLM call to generate natural, contextualized feedback
"""

from __future__ import annotations

from dataclasses import dataclass

from adr_analyser.aggregation.aggregator import AggregatedScore, QualityTier
from adr_analyser.quality_model.dimensions import QUALITY_MODEL
from adr_analyser.scoring.gemini_scorer import ADRAssessment, DimensionScore


@dataclass
class FeedbackReport:
    """Structured feedback report for a single ADR."""

    adr_filename: str
    overall_assessment: str
    tier: str
    composite_score: float
    strengths: list[str]
    improvements: list[str]
    dimension_feedback: dict[str, str]  # dim_id -> specific feedback
    weakest_section_suggestion: str | None = None


# Feedback templates keyed by (dimension_id, score)
_IMPROVEMENT_TEMPLATES: dict[tuple[str, int], str] = {
    # A1 - Completeness
    ("A1", 1): (
        "Your ADR is missing critical sections. Add at minimum: a Context section explaining "
        "the problem, a Decision section stating your choice, and a Rationale section "
        "explaining why. See MADR template for the expected structure."
    ),
    ("A1", 2): (
        "Your ADR has the basic sections but they need more substance. Expand each section "
        "beyond a single sentence. Add optional sections like Decision Drivers and "
        "Consequences (Pros/Cons) to make the record more useful."
    ),
    # A2 - Structural Conformance
    ("A2", 1): (
        "Your ADR lacks recognizable structure. Use markdown headings (## Context, ## Decision, "
        "## Rationale, ## Consequences) to organize your content. Follow the MADR template."
    ),
    ("A2", 2): (
        "Your ADR structure needs improvement. Use consistent heading levels (# for title, "
        "## for sections). Add metadata (Status, Date) and ensure sections follow a logical order."
    ),
    # B1 - Context Adequacy
    ("B1", 1): (
        "Your Context section is missing or trivial. Explain: What problem are you solving? "
        "Why does this decision matter architecturally? What are the forces/constraints "
        "driving this decision?"
    ),
    ("B1", 2): (
        "Your Context is too generic. Add project-specific details: What is your system? "
        "What requirements led to this decision? Identify at least 2-3 concrete decision "
        "drivers (e.g., performance targets, team expertise, budget constraints)."
    ),
    # B2 - Alternatives Coverage
    ("B2", 1): (
        "Your ADR only presents the chosen option without discussing alternatives. "
        "A good ADR should consider at least 2 options. Describe each alternative "
        "and explain why you evaluated and rejected the others."
    ),
    ("B2", 2): (
        "Your alternatives section needs more depth. For each option, provide enough "
        "description for a reader to understand the approach. Consider adding a comparison "
        "table evaluating each alternative against your decision drivers."
    ),
    # B3 - Rationale Depth
    ("B3", 1): (
        "Your ADR lacks a rationale. Simply stating the decision without explaining 'why' "
        "defeats the purpose of a decision record. Add a Rationale section with explicit "
        "reasoning linking your choice to specific drivers and tradeoffs."
    ),
    ("B3", 2): (
        "Your rationale is too generic. Instead of general statements like 'it is popular', "
        "connect your reasoning to your specific project context. Reference the decision "
        "drivers from your Context section and discuss tradeoffs explicitly."
    ),
    # B4 - Consequence Specificity
    ("B4", 1): (
        "Your ADR is missing a Consequences section. Add both Pros and Cons of your decision. "
        "What will improve? What risks or costs are introduced? Be specific to your project."
    ),
    ("B4", 2): (
        "Your consequences are too vague. Replace generic statements like 'better performance' "
        "with specific, project-relevant impacts (e.g., 'Reduces query latency from 800ms to "
        "200ms for product catalog pages'). Include both positive and negative consequences."
    ),
    # B5 - Decision Specificity
    ("B5", 1): (
        "Your decision is unclear or ambiguous. State explicitly: What technology/approach "
        "did you choose? What is the scope of this decision? A reader should be able to "
        "act on this decision without seeking clarification."
    ),
    ("B5", 2): (
        "Your decision needs more specificity. Include: the exact technology or approach chosen, "
        "its scope (what it applies to and what it doesn't), and the decision status "
        "(proposed, accepted, deprecated)."
    ),
    # C1 - Clarity and Readability
    ("C1", 1): (
        "Your ADR has significant readability issues. Review for grammatical correctness, "
        "clear sentence structure, and logical flow between sections. Each section should "
        "clearly serve its purpose."
    ),
    ("C1", 2): (
        "Your writing could be clearer. Ensure each sentence adds information, avoid "
        "vague language, and check that sections flow logically from Context → Decision → "
        "Rationale → Consequences."
    ),
    # C2 - Consistency
    ("C2", 1): (
        "Your ADR contains contradictions between sections. Ensure your decision drivers align "
        "with your evaluation criteria, and that your decision logically follows from your "
        "analysis. Use consistent terminology throughout."
    ),
    ("C2", 2): (
        "There are minor inconsistencies in your ADR. Check that: (1) every decision driver "
        "mentioned in Context is addressed in Rationale, (2) terminology is consistent "
        "throughout, and (3) the decision logically follows from your analysis."
    ),
    # C3 - Traceability
    ("C3", 1): (
        "Your ADR exists in isolation with no references. Add: links to relevant documentation "
        "for your chosen technology, identification of affected components or services, and "
        "references to any related decisions."
    ),
    ("C3", 2): (
        "Your traceability could be improved. Beyond basic documentation links, consider "
        "adding: which components or services are affected by this decision, any related "
        "or superseded decisions, and specific evidence (benchmarks, case studies)."
    ),
}

# Strength templates keyed by (dimension_id, score)
_STRENGTH_TEMPLATES: dict[tuple[str, int], str] = {
    ("A1", 4): "Excellent completeness—all relevant sections present with thorough content.",
    ("A1", 3): "Good completeness with all mandatory sections substantively filled.",
    ("A2", 4): "Exemplary structural conformance following the MADR template precisely.",
    ("A2", 3): "Good document structure with recognizable template adherence.",
    ("B1", 4): "Rich, detailed context with clear architectural significance and prioritized drivers.",
    ("B1", 3): "Adequate context that explains the problem with project-specific details.",
    ("B2", 4): "Thorough alternatives analysis with systematic evaluation against drivers.",
    ("B2", 3): "Good coverage of genuinely distinct alternatives with sufficient description.",
    ("B3", 4): "Exemplary rationale with evidence, tradeoff analysis, and driver connections.",
    ("B3", 3): "Adequate rationale that references specific drivers and acknowledges tradeoffs.",
    ("B4", 4): "Detailed, project-specific consequences with quantified impacts.",
    ("B4", 3): "Good consequence coverage with both pros and cons in project-specific terms.",
    ("B5", 4): "Precise, unambiguous decision with clear scope and status.",
    ("B5", 3): "Clear decision statement with specific option identified.",
    ("C1", 4): "Excellent writing quality—concise, polished, and well-structured.",
    ("C1", 3): "Good readability with clear, professional language.",
    ("C2", 4): "Perfect internal consistency with explicit driver-to-evaluation alignment.",
    ("C2", 3): "Good consistency with logical alignment between sections.",
    ("C3", 4): "Comprehensive traceability with rich links to related artifacts.",
    ("C3", 3): "Adequate traceability with external references and internal links.",
}


def generate_template_feedback(
    aggregated: AggregatedScore,
    assessment: ADRAssessment | None = None,
) -> FeedbackReport:
    """Generate feedback using templates (no LLM required).

    Args:
        aggregated: Aggregated score for the ADR.
        assessment: Optional full assessment with reasoning (for dimension-level feedback).

    Returns:
        FeedbackReport with structured feedback.
    """
    scores = aggregated.dimension_scores

    # Overall assessment
    tier_descriptions = {
        QualityTier.EXCELLENT: (
            "This ADR demonstrates excellent quality across all dimensions. "
            "It could serve as an exemplar for other decision records."
        ),
        QualityTier.GOOD: (
            "This ADR demonstrates good quality overall, with solid coverage of "
            "most quality dimensions. Some areas could be strengthened for a more "
            "comprehensive decision record."
        ),
        QualityTier.NEEDS_IMPROVEMENT: (
            "This ADR has some positive elements but needs significant improvement "
            "in several areas. Key sections are present but lack depth or specificity."
        ),
        QualityTier.POOR: (
            "This ADR requires substantial revision. Multiple critical quality "
            "dimensions are not adequately addressed. Review the improvement "
            "suggestions below and consider rewriting with the MADR template."
        ),
    }

    overall = (
        f"{tier_descriptions[aggregated.tier]} "
        f"Overall score: {aggregated.weighted_composite}/4.0 ({aggregated.tier.value})."
    )

    # Top 3 strengths (highest-scoring dimensions)
    sorted_dims = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    strengths = []
    for dim_id, score in sorted_dims[:3]:
        template = _STRENGTH_TEMPLATES.get((dim_id, score))
        if template:
            strengths.append(f"[{dim_id} — {QUALITY_MODEL[dim_id].name}] {template}")
        elif score >= 3:
            strengths.append(
                f"[{dim_id} — {QUALITY_MODEL[dim_id].name}] "
                f"Good performance (score: {score}/4)."
            )

    # Top 3 improvement suggestions (lowest-scoring dimensions)
    improvements = []
    for dim_id, score in sorted_dims[-3:]:
        if score <= 2:
            template = _IMPROVEMENT_TEMPLATES.get((dim_id, score))
            if template:
                improvements.append(
                    f"[{dim_id} — {QUALITY_MODEL[dim_id].name}, score: {score}/4] {template}"
                )
        elif score == 3:
            dim = QUALITY_MODEL[dim_id]
            improvements.append(
                f"[{dim_id} — {dim.name}, score: 3/4] "
                f"To reach an excellent score, review the scoring criteria for {dim.name} "
                f"and strengthen this section with more specific, evidence-based content."
            )

    # Dimension-level feedback
    dim_feedback = {}
    for dim_id, score in scores.items():
        dim = QUALITY_MODEL[dim_id]
        anchor = next((a for a in dim.anchors if a.score == score), None)
        if anchor:
            dim_feedback[dim_id] = f"Score {score}/4 ({anchor.label}): {anchor.description}"

        # Include LLM reasoning if available
        if assessment and dim_id in assessment.dimension_scores:
            dim_scores = assessment.dimension_scores[dim_id]
            if dim_scores:
                # Use the reasoning from the first pass
                reasoning = dim_scores[0].reasoning
                if reasoning:
                    dim_feedback[dim_id] += f"\n\nDetailed analysis: {reasoning}"

    return FeedbackReport(
        adr_filename=aggregated.adr_filename,
        overall_assessment=overall,
        tier=aggregated.tier.value,
        composite_score=aggregated.weighted_composite,
        strengths=strengths,
        improvements=improvements,
        dimension_feedback=dim_feedback,
    )


def build_llm_feedback_prompt(
    aggregated: AggregatedScore,
    dimension_reasonings: dict[str, str],
) -> str:
    """Build a prompt for LLM-enhanced feedback generation (Stage 5).

    This prompt is used for a final LLM call that synthesizes all dimension
    scores and reasoning into natural, actionable feedback.

    Args:
        aggregated: Aggregated score for the ADR.
        dimension_reasonings: Dict mapping dim_id to LLM reasoning text.

    Returns:
        Prompt string for the feedback generation LLM call.
    """
    scores_summary = "\n".join(
        f"  {dim_id} ({QUALITY_MODEL[dim_id].name}): {score}/4"
        for dim_id, score in aggregated.dimension_scores.items()
    )

    reasonings_summary = "\n\n".join(
        f"[{dim_id} — {QUALITY_MODEL[dim_id].name}]\n{reasoning}"
        for dim_id, reasoning in dimension_reasonings.items()
    )

    return f"""\
You are an expert software architecture instructor providing feedback on a student's \
Architectural Decision Record (ADR).

The ADR has been evaluated across 10 quality dimensions. Here are the scores and analysis:

SCORES:
{scores_summary}

Overall: {aggregated.weighted_composite}/4.0 ({aggregated.tier.value})
Weakest dimension: {aggregated.min_dimension} ({QUALITY_MODEL[aggregated.min_dimension].name})

DETAILED ANALYSIS PER DIMENSION:
{reasonings_summary}

Based on this analysis, generate a constructive feedback report in JSON format with:
{{
  "overall_assessment": "2-3 sentence summary of the ADR's quality",
  "strengths": ["top 3 specific strengths with evidence from the ADR"],
  "improvements": ["top 3 specific, actionable improvement suggestions with references to rubric criteria"],
  "weakest_section_revision": "A concrete suggestion for how to improve the weakest section, with an example of what better content might look like"
}}

GUIDELINES:
- Be constructive and specific—generic advice is not helpful.
- Reference actual content from the ADR in your feedback.
- Frame improvements as learning opportunities, not criticisms.
- Prioritize the most impactful improvements.
"""
