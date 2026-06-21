"""The one content-quality judge — locked rubric + deterministic guards.

Trust design (CLAUDE.md "honest instruments"; MASTERPLAN I8). The P0 run scored a
suspicious 25/25 because the judge was the SAME model as the generator with a
free-floating rubric. This module fixes that:

  1. **Judge ≠ generator.** Default judge = Sonnet 4.6, distinct from the Opus 4.8
     generator. (Within an Anthropic-only gateway this is a different *model*, not a
     different *provider* — it curbs same-model self-preference but not cross-family
     bias. A cross-provider judge is deferred to P6's red-team harness; honest limit.)
  2. **Locked rubric bands.** Each criterion has explicit 0-5 descriptors so the
     judge scores against fixed anchors instead of vibes.
  3. **Deterministic guards run regardless of the judge.** A hard guard failure
     (missing section, banned compliance claim) FAILS the gate no matter the score —
     the gate is never 100% judge-dependent.

`judge_content()` is pure of the pipeline/DB so the calibration harness
(scripts/check-eval-gate.py) can exercise it directly.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from tools.pipeline.context import brand_summary, parse_step_json
from tools.utils import claude_client

# Different model from the Opus 4.8 generator — the core anti-self-leniency lever.
DEFAULT_JUDGE_MODEL = "claude-sonnet-4-6"

CRITERIA = ["brand_fit", "hook_strength", "clarity", "cta_strength", "platform_fit"]

# Locked 0-5 band anchors — the judge scores against these, not free-form.
_BANDS = """Score each criterion as an integer 0-5 against these fixed anchors:
- brand_fit:     0 off-brand/contradicts the voice · 2 generic, not clearly this brand · 4 on-brand · 5 unmistakably this brand & audience
- hook_strength: 0 no hook · 2 weak/generic opener · 4 strong scroll-stopper · 5 exceptional pattern-interrupt
- clarity:       0 confusing · 2 somewhat unclear · 4 clear · 5 effortless, crystal clear
- cta_strength:  0 no CTA · 2 vague CTA · 4 one clear CTA · 5 compelling, specific, low-friction (e.g. WhatsApp)
- platform_fit:  0 wrong format for the platform · 2 acceptable · 4 well-suited · 5 native to the platform's norms
total = the sum of the five (0-25). Score honestly and do not inflate; most competent-but-unremarkable content lands 12-17."""

_SYSTEM = (
    "You are a strict, experienced content QA reviewer at a marketing agency. You "
    "calibrate to the rubric's anchors exactly and refuse to inflate scores."
)

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "object",
            "properties": {c: {"type": "integer"} for c in CRITERIA},
            "required": CRITERIA,
            "additionalProperties": False,
        },
        "total": {"type": "integer"},
        "notes": {"type": "string"},
    },
    "required": ["scores", "total", "notes"],
    "additionalProperties": False,
}


# ── Deterministic guards ────────────────────────────────────────────────────────
@dataclass(frozen=True)
class GuardFailure:
    name: str
    hard: bool
    detail: str


# Starter compliance/quality bans. The FULL per-country compliance engine is P3;
# these are the always-block basics relevant to Gulf travel content.
_BANNED_HARD = [
    ("alcohol_gambling",
     re.compile(r"\b(alcohol|wine|beer|whisky|vodka|cocktail|casino|gambl\w*|nightclub|pub\b)\b"
                r"|خمر|كحول|كازينو|قمار", re.IGNORECASE)),
    ("false_guarantee",
     re.compile(r"\b(guaranteed|100%\s*guarantee|risk[- ]free|no\s+risk)\b", re.IGNORECASE)),
]
_CAPTION_MAX = 2200  # Instagram caption hard limit; a sane upper bound for all platforms.


def run_guards(script: str, caption: str) -> list[GuardFailure]:
    """Deterministic checks that do not depend on the judge. Hard failures block
    publication regardless of the rubric score."""
    out: list[GuardFailure] = []
    if not (script or "").strip():
        out.append(GuardFailure("required_script", True, "script is empty"))
    if not (caption or "").strip():
        out.append(GuardFailure("required_caption", True, "caption is empty"))
    if len(caption or "") > _CAPTION_MAX:
        out.append(GuardFailure("caption_length", False,
                                f"caption {len(caption)} chars > {_CAPTION_MAX}"))
    blob = f"{script}\n{caption}"
    for name, pat in _BANNED_HARD:
        m = pat.search(blob)
        if m:
            out.append(GuardFailure(f"banned:{name}", True, f"matched {m.group(0)!r}"))
    return out


def judge_content(
    *,
    brand: dict[str, Any],
    script: str,
    caption: str,
    platform: str,
    min_score: int = 18,
    max_score: int = 25,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    brand_id: str | None = None,
    run_id: str | None = None,
    budget_usd: float | None = None,
) -> dict[str, Any]:
    """Score one artifact. Returns a verdict dict. Pure of the DB; the LLM cost is
    logged to the ledger (category 'eval'), accumulating onto run_id when given."""
    guards = run_guards(script, caption)
    hard_failures = [g for g in guards if g.hard]

    prompt = (
        f"{brand_summary(brand)}\n\n"
        f"Content to review (platform: {platform}):\n"
        f"SCRIPT:\n{script}\n\n"
        f"CAPTION:\n{caption}\n\n"
        f"{_BANDS}\n\n`notes` = one sentence naming the single weakest dimension."
    )
    res = claude_client.complete(
        prompt=prompt,
        system=_SYSTEM,
        model=judge_model,
        max_tokens=700,
        json_schema=JUDGE_SCHEMA,
        agent_type="ANALYTICS_SAFETY",
        category="eval",
        tool_name="eval.judge",
        brand_id=brand_id,
        run_id=run_id,
        budget_usd=budget_usd,
    )
    data = parse_step_json(res.text, res.stop_reason)
    total = int(data["total"])
    passed = total >= min_score and not hard_failures

    return {
        "total": total,
        "max_score": max_score,
        "min_score": min_score,
        "passed": passed,
        "scores": data.get("scores", {}),
        "notes": str(data.get("notes", "")),
        "judge_model": res.model,
        "guard_failures": [{"name": g.name, "hard": g.hard, "detail": g.detail} for g in guards],
        "hard_failed": bool(hard_failures),
        "cost_usd": res.cost_usd,
    }
