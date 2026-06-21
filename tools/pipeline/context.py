"""Shared state passed through a pipeline run, plus the JSON extractor steps use
to parse model output.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineContext:
    """Threaded through every step of one run.

    The runner sets `step_name` / `agent_type` / `step_config` before each step;
    steps read prior results from `outputs[<earlier step name>]` and write their
    own result dict back under their own name.
    """
    brand_id: str
    user_id: str
    run_id: str
    seed: str
    brand: dict[str, Any]
    budget_usd: float
    outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    # set per-step by the runner
    step_name: str = ""
    agent_type: str = "ORCHESTRATOR"
    step_config: dict[str, Any] = field(default_factory=dict)

    def out(self, step: str) -> dict[str, Any]:
        """Result dict of an earlier step (raises if it hasn't run)."""
        try:
            return self.outputs[step]
        except KeyError as exc:
            raise KeyError(
                f"Step {self.step_name!r} needs output of {step!r}, which has not run."
            ) from exc


class BadModelJSON(ValueError):
    """The model did not return parseable JSON where a step required it."""


class OutputTruncated(BadModelJSON):
    """The reply hit max_tokens before the JSON closed — raise the step's ceiling."""


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def extract_json(text: str) -> dict[str, Any]:
    """Parse a JSON object out of a model response.

    Tolerates ```json code fences and leading/trailing prose by falling back to
    the outermost `{...}` span. Raises BadModelJSON if nothing parses.
    """
    stripped = _FENCE.sub("", text).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    start, end = stripped.find("{"), stripped.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(stripped[start : end + 1])
        except json.JSONDecodeError as exc:
            raise BadModelJSON(
                f"Could not parse JSON from model output: {exc}. Head: {stripped[:200]!r}"
            ) from exc
    raise BadModelJSON(f"Model output contained no JSON object. Head: {stripped[:200]!r}")


def parse_step_json(text: str, stop_reason: str | None) -> dict[str, Any]:
    """Parse a step's JSON reply, distinguishing a truncated reply (hit
    max_tokens) from genuinely-malformed output so the failure is actionable."""
    if stop_reason == "max_tokens":
        raise OutputTruncated(
            f"Reply hit max_tokens before the JSON closed — raise this step's "
            f"max_tokens. Head: {text[:160]!r}"
        )
    return extract_json(text)


def brand_summary(brand: dict[str, Any]) -> str:
    """One-paragraph brand context block for prompts."""
    tone = ", ".join(brand.get("voiceTone") or []) or "unspecified"
    regions = ", ".join(brand.get("targetRegions") or []) or "unspecified"
    return (
        f"Brand: {brand.get('name')} (vertical: {brand.get('vertical')}). "
        f"Language: {brand.get('language')}. Target regions: {regions}. "
        f"Voice tone: {tone}. Target persona: {brand.get('targetPersona') or 'unspecified'}."
    )
