"""
Gemini-based ADR scorer using the Vertex AI / Google Generative AI API.

Implements Stage 3 of the pipeline: per-dimension scoring using LLM-as-Judge.

Supports two modes:
1. Online prediction: individual API calls (for development/debugging)
2. Batch prediction: JSONL-based batch processing via Vertex AI (for production)

Key design decisions from the research plan:
- temperature=0 for maximum determinism
- Structured JSON output via response_schema
- Separate LLM call per dimension (G-Eval best practice)
- 5 inference passes per ADR to quantify non-determinism
- Median score as final assessment
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from adr_analyser.quality_model.dimensions import DIMENSION_ORDER, QUALITY_MODEL
from adr_analyser.quality_model.rubric import SCORING_RUBRIC
from adr_analyser.scoring.prompts import (
    SCORING_SCHEMA,
    SYSTEM_INSTRUCTION,
    build_scoring_user_message,
    get_all_dimension_prompts,
)


@dataclass
class DimensionScore:
    """Score for a single dimension on a single ADR."""

    dimension_id: str
    dimension_name: str
    score: int
    reasoning: str
    evidence: list[str]
    confidence: str
    pass_number: int = 1  # Which inference pass (1-5)


@dataclass
class ADRAssessment:
    """Complete assessment of a single ADR across all dimensions."""

    adr_filename: str
    adr_content: str
    dimension_scores: dict[str, list[DimensionScore]]  # dim_id -> list of scores (one per pass)

    @property
    def median_scores(self) -> dict[str, int]:
        """Compute median score per dimension across all passes."""
        import statistics

        result = {}
        for dim_id, scores in self.dimension_scores.items():
            values = [s.score for s in scores]
            result[dim_id] = int(statistics.median(values))
        return result

    @property
    def score_std(self) -> dict[str, float]:
        """Compute standard deviation per dimension across passes."""
        import statistics

        result = {}
        for dim_id, scores in self.dimension_scores.items():
            values = [s.score for s in scores]
            result[dim_id] = statistics.stdev(values) if len(values) > 1 else 0.0
        return result


class GeminiScorer:
    """Score ADRs using Google's Gemini model.

    Args:
        model_name: Gemini model identifier (e.g., "gemini-2.0-flash").
        temperature: Sampling temperature (0 for deterministic).
        num_passes: Number of inference passes per ADR for stability analysis.
        use_vertex_ai: If True, use Vertex AI SDK; if False, use google-generativeai.
        project_id: GCP project ID (required if use_vertex_ai=True).
        location: GCP region (required if use_vertex_ai=True).
    """

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.0,
        num_passes: int = 5,
        use_vertex_ai: bool = False,
        project_id: Optional[str] = None,
        location: str = "europe-west4",
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.num_passes = num_passes
        self.use_vertex_ai = use_vertex_ai
        self.project_id = project_id
        self.location = location
        self._dimension_prompts = get_all_dimension_prompts()
        self._client = None

    def _get_client(self):
        """Lazily initialize the API client."""
        if self._client is not None:
            return self._client

        if self.use_vertex_ai:
            import google.cloud.aiplatform as aiplatform
            from vertexai.generative_models import GenerativeModel

            aiplatform.init(project=self.project_id, location=self.location)
            self._client = GenerativeModel(
                self.model_name,
                system_instruction=SYSTEM_INSTRUCTION,
            )
        else:
            import google.generativeai as genai

            self._client = genai.GenerativeModel(
                self.model_name,
                system_instruction=SYSTEM_INSTRUCTION,
            )
        return self._client

    def score_dimension(
        self,
        adr_content: str,
        dimension_id: str,
        pass_number: int = 1,
    ) -> DimensionScore:
        """Score a single ADR on a single dimension.

        Args:
            adr_content: The full ADR markdown content.
            dimension_id: Dimension to score (e.g., "A1", "B3").
            pass_number: Which inference pass this is (1-5).

        Returns:
            DimensionScore with the assessment result.
        """
        dim_prompt = self._dimension_prompts[dimension_id]
        user_message = build_scoring_user_message(adr_content, dim_prompt)

        model = self._get_client()

        generation_config = {
            "temperature": self.temperature,
            "response_mime_type": "application/json",
            "response_schema": SCORING_SCHEMA,
        }

        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [{"text": user_message}]},
            ],
            generation_config=generation_config,
        )

        # Parse the JSON response
        result = json.loads(response.text)

        return DimensionScore(
            dimension_id=result["dimension_id"],
            dimension_name=result["dimension_name"],
            score=int(result["score"]),
            reasoning=result["reasoning"],
            evidence=result.get("evidence", []),
            confidence=result.get("confidence", "medium"),
            pass_number=pass_number,
        )

    def score_adr(
        self,
        adr_content: str,
        adr_filename: str,
        dimensions: Optional[list[str]] = None,
    ) -> ADRAssessment:
        """Score a single ADR across all (or specified) dimensions with multiple passes.

        Args:
            adr_content: The full ADR markdown content.
            adr_filename: Filename for identification.
            dimensions: List of dimension IDs to score. Defaults to all 10.

        Returns:
            ADRAssessment with scores for all dimensions across all passes.
        """
        dims = dimensions or DIMENSION_ORDER
        assessment = ADRAssessment(
            adr_filename=adr_filename,
            adr_content=adr_content,
            dimension_scores={d: [] for d in dims},
        )

        for pass_num in range(1, self.num_passes + 1):
            for dim_id in dims:
                try:
                    score = self.score_dimension(adr_content, dim_id, pass_num)
                    assessment.dimension_scores[dim_id].append(score)
                except Exception as e:
                    print(f"Warning: Failed to score {adr_filename} on {dim_id} "
                          f"(pass {pass_num}): {e}")
                # Rate limiting: brief pause between calls
                time.sleep(0.1)

        return assessment

    def generate_batch_input(
        self,
        adrs: list[tuple[str, str]],  # (filename, content) pairs
        output_path: str | Path,
        dimensions: Optional[list[str]] = None,
    ) -> Path:
        """Generate JSONL batch input for Vertex AI Batch Prediction.

        Creates a JSONL file where each line is a batch request for
        one ADR × one dimension × one pass.

        Args:
            adrs: List of (filename, content) tuples.
            output_path: Path to write the JSONL file.
            dimensions: Dimensions to score. Defaults to all 10.

        Returns:
            Path to the generated JSONL file.
        """
        output_path = Path(output_path)
        dims = dimensions or DIMENSION_ORDER

        with open(output_path, "w") as f:
            for filename, content in adrs:
                for dim_id in dims:
                    dim_prompt = self._dimension_prompts[dim_id]
                    user_message = build_scoring_user_message(content, dim_prompt)

                    for pass_num in range(1, self.num_passes + 1):
                        request = {
                            "request_id": f"{filename}__{dim_id}__pass{pass_num}",
                            "model": f"publishers/google/models/{self.model_name}",
                            "contents": [
                                {
                                    "role": "user",
                                    "parts": [{"text": user_message}],
                                }
                            ],
                            "system_instruction": {
                                "parts": [{"text": SYSTEM_INSTRUCTION}]
                            },
                            "generation_config": {
                                "temperature": self.temperature,
                                "response_mime_type": "application/json",
                                "response_schema": SCORING_SCHEMA,
                            },
                        }
                        f.write(json.dumps(request) + "\n")

        total_requests = len(adrs) * len(dims) * self.num_passes
        print(f"Generated {total_requests} batch requests to {output_path}")
        return output_path

    @staticmethod
    def parse_batch_output(output_path: str | Path) -> dict[str, ADRAssessment]:
        """Parse Vertex AI batch prediction output JSONL.

        Args:
            output_path: Path to the batch output JSONL file.

        Returns:
            Dict mapping filename to ADRAssessment.
        """
        output_path = Path(output_path)
        assessments: dict[str, ADRAssessment] = {}

        with open(output_path) as f:
            for line in f:
                result = json.loads(line)
                request_id = result.get("request_id", "")

                # Parse request_id: filename__dim_id__passN
                parts = request_id.split("__")
                if len(parts) != 3:
                    print(f"Warning: Unexpected request_id format: {request_id}")
                    continue

                filename, dim_id, pass_str = parts
                pass_num = int(pass_str.replace("pass", ""))

                # Get or create assessment
                if filename not in assessments:
                    assessments[filename] = ADRAssessment(
                        adr_filename=filename,
                        adr_content="",
                        dimension_scores={d: [] for d in DIMENSION_ORDER},
                    )

                # Parse the response
                try:
                    response_text = (
                        result.get("response", {})
                        .get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "{}")
                    )
                    score_data = json.loads(response_text)
                    score = DimensionScore(
                        dimension_id=dim_id,
                        dimension_name=score_data.get("dimension_name", ""),
                        score=int(score_data["score"]),
                        reasoning=score_data.get("reasoning", ""),
                        evidence=score_data.get("evidence", []),
                        confidence=score_data.get("confidence", "medium"),
                        pass_number=pass_num,
                    )
                    assessments[filename].dimension_scores[dim_id].append(score)
                except (KeyError, json.JSONDecodeError, IndexError) as e:
                    print(f"Warning: Failed to parse result for {request_id}: {e}")

        return assessments
