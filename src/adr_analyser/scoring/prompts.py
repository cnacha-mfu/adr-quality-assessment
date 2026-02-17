"""
Prompt templates for per-dimension LLM scoring.

Following the G-Eval framework (Liu et al., EMNLP 2023):
- Evaluate each quality dimension in a separate LLM call
- Single-aspect evaluation for higher reliability
- Chain-of-thought instruction before scoring
- Structured JSON output with score, reasoning, and evidence

Each prompt includes:
1. System instruction with role definition and rubric
2. Dimension-specific scoring criteria with anchored scale
3. Few-shot example(s) at different quality levels
4. Chain-of-thought instruction
5. JSON output schema specification
"""

from __future__ import annotations

from adr_analyser.quality_model.dimensions import QUALITY_MODEL, QualityDimension
from adr_analyser.quality_model.rubric import SCORING_RUBRIC, DimensionRubric

# JSON output schema enforced via Gemini structured output mode
SCORING_SCHEMA = {
    "type": "object",
    "properties": {
        "dimension_id": {"type": "string", "description": "Dimension identifier (e.g., A1, B3)"},
        "dimension_name": {"type": "string", "description": "Dimension name"},
        "score": {
            "type": "integer",
            "description": "Quality score on 4-point scale (1, 2, 3, or 4)",
        },
        "reasoning": {
            "type": "string",
            "description": (
                "Step-by-step analysis of the ADR against the scoring criteria, "
                "explaining how each criterion was evaluated before arriving at the score."
            ),
        },
        "evidence": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Specific quotes or references from the ADR that support the assigned score."
            ),
        },
        "confidence": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "Confidence in the assigned score.",
        },
    },
    "required": ["dimension_id", "dimension_name", "score", "reasoning", "evidence", "confidence"],
}

SYSTEM_INSTRUCTION = """\
You are an expert software architecture reviewer specializing in Architectural Decision Records (ADRs). \
Your task is to evaluate the quality of a student-written ADR on a single specific quality dimension.

IMPORTANT GUIDELINES:
- Rate what is written, not what was intended. Score based on explicit content only.
- These are student assignments, not production ADRs. Calibrate accordingly, but apply the rubric consistently.
- A score of 4 represents genuinely excellent work by student standards.
- Sample/example code sections are supplementary and should not influence quality ratings.
- Rate communication effectiveness, not native-speaker fluency.
- Use the chain-of-thought approach: first analyze the ADR against each criterion in the rubric, then assign a score.
- Your output MUST be valid JSON matching the specified schema.
"""


def build_dimension_prompt(dim: QualityDimension, rubric: DimensionRubric) -> str:
    """Build the dimension-specific scoring prompt (used as part of the user message).

    This is the reusable portion that goes into the system instruction cache.
    """
    # Build scale anchors text
    anchors_text = "\n".join(
        f"  {a.score} — {a.label}: {a.description}" for a in dim.anchors
    )

    # Build GQM questions
    questions_text = "\n".join(f"  - {q}" for q in dim.gqm.questions)

    # Build few-shot examples (use 2: one low, one high)
    examples = rubric.anchor_examples
    low_example = examples[0]  # score 1
    high_example = examples[-1]  # score 4

    examples_text = f"""
--- FEW-SHOT EXAMPLE (Score {low_example.score}) ---
ADR Excerpt:
{low_example.excerpt}

Expected output:
{{
  "dimension_id": "{dim.id}",
  "dimension_name": "{dim.name}",
  "score": {low_example.score},
  "reasoning": "{low_example.annotation_notes}",
  "evidence": ["(relevant quote from excerpt)"],
  "confidence": "high"
}}

--- FEW-SHOT EXAMPLE (Score {high_example.score}) ---
ADR Excerpt:
{high_example.excerpt}

Expected output:
{{
  "dimension_id": "{dim.id}",
  "dimension_name": "{dim.name}",
  "score": {high_example.score},
  "reasoning": "{high_example.annotation_notes}",
  "evidence": ["(relevant quote from excerpt)"],
  "confidence": "high"
}}
"""

    prompt = f"""\
DIMENSION: {dim.id} — {dim.name}
CATEGORY: {dim.category.value.title()} Quality

DEFINITION:
{dim.definition}

SCORING INSTRUCTIONS:
{rubric.scoring_instructions}

EVALUATION QUESTIONS (consider each before scoring):
{questions_text}

SCORING SCALE (use ONLY these values: 1, 2, 3, or 4):
{anchors_text}

{examples_text}

CHAIN-OF-THOUGHT INSTRUCTIONS:
1. Read the full ADR carefully.
2. For each evaluation question above, note what the ADR does or does not provide.
3. Compare your observations against the scale anchors.
4. Select the score that best matches the ADR's quality on this dimension.
5. Provide specific evidence (quotes from the ADR) supporting your score.
6. Output your assessment as a JSON object.
"""
    return prompt


def build_scoring_user_message(adr_content: str, dimension_prompt: str) -> str:
    """Build the complete user message for scoring a single ADR on a single dimension."""
    return f"""\
{dimension_prompt}

--- ADR TO EVALUATE ---
{adr_content}
--- END OF ADR ---

Now evaluate this ADR on the specified dimension. Think step-by-step through the evaluation \
questions, then provide your JSON assessment."""


def get_all_dimension_prompts() -> dict[str, str]:
    """Pre-build all 10 dimension prompts for caching.

    Returns:
        Dict mapping dimension_id to the dimension-specific prompt text.
    """
    prompts = {}
    for dim_id, dim in QUALITY_MODEL.items():
        rubric = SCORING_RUBRIC[dim_id]
        prompts[dim_id] = build_dimension_prompt(dim, rubric)
    return prompts
