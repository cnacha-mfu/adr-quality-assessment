"""
Open-source LLM scorer using OpenAI-compatible APIs.

Supports any model accessible via an OpenAI-compatible endpoint:
- Cloud providers: Groq (Llama 3.3 70B), Cerebras (Qwen 3 235B)
- Self-hosted: vLLM, Ollama, etc.

All use identical prompts and scoring schemas as the Gemini scorer
to enable fair comparison in RQ1 cross-model agreement.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from adr_analyser.quality_model.dimensions import DIMENSION_ORDER
from adr_analyser.scoring.gemini_scorer import ADRAssessment, DimensionScore
from adr_analyser.scoring.prompts import (
    SYSTEM_INSTRUCTION,
    build_scoring_user_message,
    get_all_dimension_prompts,
)


class VLLMScorer:
    """Score ADRs using models served via OpenAI-compatible APIs.

    Works with cloud providers (Groq, Cerebras) and self-hosted servers (vLLM).

    Args:
        model_name: Model identifier for the API (e.g., "llama-3.3-70b-versatile").
        api_base: API endpoint URL.
        api_key: API key (use "EMPTY" for local vLLM servers).
        temperature: Sampling temperature (0 for deterministic).
        num_passes: Number of inference passes per ADR.
        max_tokens: Maximum tokens for the response.
    """

    def __init__(
        self,
        model_name: str = "prometheus-eval/prometheus-7b-v2.0",
        api_base: str = "http://localhost:8000/v1",
        api_key: str = "EMPTY",
        temperature: float = 0.0,
        num_passes: int = 5,
        max_tokens: int = 2048,
    ):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key
        self.temperature = temperature
        self.num_passes = num_passes
        self.max_tokens = max_tokens
        self._dimension_prompts = get_all_dimension_prompts()
        self._client = None

    def _get_client(self):
        """Lazily initialize the OpenAI client."""
        if self._client is not None:
            return self._client

        from openai import OpenAI

        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
        )
        return self._client

    def score_dimension(
        self,
        adr_content: str,
        dimension_id: str,
        pass_number: int = 1,
    ) -> DimensionScore:
        """Score a single ADR on a single dimension using vLLM-served model.

        Args:
            adr_content: The full ADR markdown content.
            dimension_id: Dimension to score (e.g., "A1").
            pass_number: Which inference pass this is.

        Returns:
            DimensionScore with the assessment result.
        """
        dim_prompt = self._dimension_prompts[dimension_id]
        user_message = build_scoring_user_message(adr_content, dim_prompt)

        client = self._get_client()

        kwargs = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_message},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        # Only request JSON mode for providers that support it
        # (some thinking models like Qwen 3 ignore response_format)
        if "cerebras" not in self.api_base:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)

        response_text = response.choices[0].message.content or ""

        # Parse JSON from the response (may need cleanup for some models)
        result = _extract_json(response_text)

        return DimensionScore(
            dimension_id=dimension_id,
            dimension_name=result.get("dimension_name", dimension_id),
            score=_clamp_score(result.get("score", 2)),
            reasoning=result.get("reasoning", ""),
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
        """Score a single ADR across all dimensions with multiple passes."""
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
                    print(
                        f"Warning: Failed to score {adr_filename} on {dim_id} "
                        f"(pass {pass_num}): {e}"
                    )
                time.sleep(0.05)  # Lighter rate limiting for local inference

        return assessment

    def generate_batch_input(
        self,
        adrs: list[tuple[str, str]],
        output_path: str | Path,
        dimensions: Optional[list[str]] = None,
    ) -> Path:
        """Generate JSONL batch input in OpenAI Batch API format.

        Each line is a JSON object with custom_id, method, url, and body.
        Compatible with OpenAI Batch API and self-hosted vLLM batch endpoints.
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
                            "custom_id": f"{filename}__{dim_id}__pass{pass_num}",
                            "method": "POST",
                            "url": "/v1/chat/completions",
                            "body": {
                                "model": self.model_name,
                                "messages": [
                                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                                    {"role": "user", "content": user_message},
                                ],
                                "temperature": self.temperature,
                                "max_tokens": self.max_tokens,
                                "response_format": {"type": "json_object"},
                            },
                        }
                        f.write(json.dumps(request) + "\n")

        total_requests = len(adrs) * len(dims) * self.num_passes
        print(f"Generated {total_requests} batch requests to {output_path}")
        return output_path

    @staticmethod
    def parse_batch_output(output_path: str | Path) -> dict[str, ADRAssessment]:
        """Parse OpenAI Batch API output JSONL.

        Returns:
            Dict mapping filename to ADRAssessment.
        """
        output_path = Path(output_path)
        assessments: dict[str, ADRAssessment] = {}

        with open(output_path) as f:
            for line in f:
                result = json.loads(line)
                custom_id = result.get("custom_id", "")

                parts = custom_id.split("__")
                if len(parts) != 3:
                    print(f"Warning: Unexpected custom_id format: {custom_id}")
                    continue

                filename, dim_id, pass_str = parts
                pass_num = int(pass_str.replace("pass", ""))

                if filename not in assessments:
                    assessments[filename] = ADRAssessment(
                        adr_filename=filename,
                        adr_content="",
                        dimension_scores={d: [] for d in DIMENSION_ORDER},
                    )

                try:
                    response_body = result.get("response", {}).get("body", {})
                    content = response_body["choices"][0]["message"]["content"]
                    score_data = _extract_json(content)
                    score = DimensionScore(
                        dimension_id=dim_id,
                        dimension_name=score_data.get("dimension_name", ""),
                        score=_clamp_score(score_data.get("score", 2)),
                        reasoning=score_data.get("reasoning", ""),
                        evidence=score_data.get("evidence", []),
                        confidence=score_data.get("confidence", "medium"),
                        pass_number=pass_num,
                    )
                    assessments[filename].dimension_scores[dim_id].append(score)
                except (KeyError, json.JSONDecodeError, IndexError) as e:
                    print(f"Warning: Failed to parse result for {custom_id}: {e}")

        return assessments


def _extract_json(text: str) -> dict:
    """Extract JSON object from model response, handling common formatting issues."""
    import re

    # Strip thinking tags (Qwen 3 models wrap output in <think>...</think>)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE)
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the text
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback: return minimal valid structure
    return {
        "score": 2,
        "reasoning": f"Failed to parse model response: {text[:200]}",
        "evidence": [],
        "confidence": "low",
    }


def _clamp_score(score) -> int:
    """Ensure score is an integer in [1, 4]."""
    try:
        s = int(score)
        return max(1, min(4, s))
    except (ValueError, TypeError):
        return 2
