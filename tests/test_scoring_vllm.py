"""Tests for VLLMScorer: api_key configuration, batch I/O, and helper functions."""

import json

from adr_analyser.scoring.vllm_scorer import VLLMScorer, _extract_json, _clamp_score


# --- _clamp_score tests ---


def test_clamp_score_valid_range():
    assert _clamp_score(1) == 1
    assert _clamp_score(2) == 2
    assert _clamp_score(3) == 3
    assert _clamp_score(4) == 4


def test_clamp_score_below_range():
    assert _clamp_score(0) == 1
    assert _clamp_score(-1) == 1
    assert _clamp_score(-100) == 1


def test_clamp_score_above_range():
    assert _clamp_score(5) == 4
    assert _clamp_score(100) == 4


def test_clamp_score_invalid_type():
    assert _clamp_score("bad") == 2
    assert _clamp_score(None) == 2
    assert _clamp_score([]) == 2


def test_clamp_score_float_conversion():
    assert _clamp_score(3.7) == 3
    assert _clamp_score("2") == 2


# --- _extract_json tests ---


def test_extract_json_valid():
    result = _extract_json('{"score": 3, "reasoning": "good"}')
    assert result["score"] == 3
    assert result["reasoning"] == "good"


def test_extract_json_with_surrounding_text():
    text = 'Here is my assessment: {"score": 4, "reasoning": "excellent"} end.'
    result = _extract_json(text)
    assert result["score"] == 4


def test_extract_json_fallback():
    result = _extract_json("this is not json at all")
    assert result["score"] == 2
    assert result["confidence"] == "low"


def test_extract_json_whitespace():
    result = _extract_json('  \n {"score": 1}  \n ')
    assert result["score"] == 1


# --- VLLMScorer constructor tests ---


def test_api_key_default():
    scorer = VLLMScorer()
    assert scorer.api_key == "EMPTY"


def test_api_key_configurable():
    scorer = VLLMScorer(api_key="my-secret-key")
    assert scorer.api_key == "my-secret-key"


def test_api_base_configurable():
    scorer = VLLMScorer(api_base="https://api.groq.com/openai/v1")
    assert scorer.api_base == "https://api.groq.com/openai/v1"


def test_model_name_configurable():
    scorer = VLLMScorer(model_name="llama-3.3-70b-versatile")
    assert scorer.model_name == "llama-3.3-70b-versatile"


# --- generate_batch_input tests ---


def test_generate_batch_input_format(tmp_path):
    """Batch input should produce valid OpenAI Batch API JSONL."""
    scorer = VLLMScorer(
        model_name="test-model",
        api_key="test-key",
        num_passes=1,
    )
    adrs = [("adr1.md", "# Title\n\nSome ADR content")]
    output = tmp_path / "batch.jsonl"
    scorer.generate_batch_input(adrs, output, dimensions=["A1"])

    lines = output.read_text().strip().split("\n")
    assert len(lines) == 1  # 1 ADR * 1 dim * 1 pass

    request = json.loads(lines[0])
    assert request["custom_id"] == "adr1.md__A1__pass1"
    assert request["method"] == "POST"
    assert request["url"] == "/v1/chat/completions"
    assert request["body"]["model"] == "test-model"
    assert request["body"]["response_format"] == {"type": "json_object"}
    assert len(request["body"]["messages"]) == 2
    assert request["body"]["messages"][0]["role"] == "system"
    assert request["body"]["messages"][1]["role"] == "user"


def test_generate_batch_input_multiple_passes(tmp_path):
    """Multiple passes should generate separate requests per pass."""
    scorer = VLLMScorer(model_name="test", num_passes=3)
    adrs = [("adr1.md", "content")]
    output = tmp_path / "batch.jsonl"
    scorer.generate_batch_input(adrs, output, dimensions=["A1", "B1"])

    lines = output.read_text().strip().split("\n")
    # 1 ADR * 2 dims * 3 passes = 6
    assert len(lines) == 6

    ids = [json.loads(line)["custom_id"] for line in lines]
    assert "adr1.md__A1__pass1" in ids
    assert "adr1.md__A1__pass3" in ids
    assert "adr1.md__B1__pass2" in ids


def test_generate_batch_input_all_dimensions(tmp_path):
    """Without explicit dimensions, all 10 should be used."""
    scorer = VLLMScorer(model_name="test", num_passes=1)
    adrs = [("adr1.md", "content")]
    output = tmp_path / "batch.jsonl"
    scorer.generate_batch_input(adrs, output)

    lines = output.read_text().strip().split("\n")
    assert len(lines) == 10  # 1 ADR * 10 dims * 1 pass


# --- parse_batch_output tests ---


def test_parse_batch_output(tmp_path):
    """Should reconstruct ADRAssessment from OpenAI batch output format."""
    output_file = tmp_path / "output.jsonl"

    batch_result = {
        "custom_id": "adr1.md__A1__pass1",
        "response": {
            "body": {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "dimension_id": "A1",
                            "dimension_name": "Completeness",
                            "score": 3,
                            "reasoning": "Good coverage",
                            "evidence": ["quote1"],
                            "confidence": "high",
                        })
                    }
                }]
            }
        },
    }
    output_file.write_text(json.dumps(batch_result) + "\n")

    assessments = VLLMScorer.parse_batch_output(output_file)
    assert "adr1.md" in assessments
    assert len(assessments["adr1.md"].dimension_scores["A1"]) == 1
    score = assessments["adr1.md"].dimension_scores["A1"][0]
    assert score.score == 3
    assert score.dimension_id == "A1"
    assert score.pass_number == 1


def test_parse_batch_output_malformed_skips(tmp_path):
    """Malformed responses should be skipped with a warning, not crash."""
    output_file = tmp_path / "output.jsonl"

    lines = [
        json.dumps({"custom_id": "bad_format", "response": {}}),
        json.dumps({
            "custom_id": "adr1.md__A1__pass1",
            "response": {"body": {"choices": [{"message": {"content": "not json"}}]}},
        }),
    ]
    output_file.write_text("\n".join(lines) + "\n")

    assessments = VLLMScorer.parse_batch_output(output_file)
    # The malformed one gets a fallback score of 2
    assert "adr1.md" in assessments
    score = assessments["adr1.md"].dimension_scores["A1"][0]
    assert score.score == 2  # fallback from _extract_json
