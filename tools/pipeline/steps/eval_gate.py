"""Step 4 — eval gate. Score the content against a 25-point rubric. A score at or
above the floor (default 18/25) marks the ContentPiece publishable (IN_REVIEW);
below the floor it is marked FAILED — the hard pre-publish floor.

This is a quality floor, not a system error: a sub-floor score does not fail the
*run* (the pipeline executed), it fails the *artifact*. The run records the
verdict in its outputData.
"""
from __future__ import annotations

from typing import Any

from tools.pipeline.context import PipelineContext, brand_summary, parse_step_json
from tools.utils import claude_client
from tools.utils.db import connect

_SYSTEM = (
    "You are a strict content QA reviewer at a marketing agency. Score honestly; "
    "do not inflate."
)

_RUBRIC = (
    "Score each criterion 0-5 (integer): brand_fit, hook_strength, clarity, "
    "cta_strength, platform_fit. total is their sum (0-25)."
)

_CRITERIA = ["brand_fit", "hook_strength", "clarity", "cta_strength", "platform_fit"]
_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "object",
            "properties": {c: {"type": "integer"} for c in _CRITERIA},
            "required": _CRITERIA,
            "additionalProperties": False,
        },
        "total": {"type": "integer"},
        "notes": {"type": "string"},
    },
    "required": ["scores", "total", "notes"],
    "additionalProperties": False,
}


def run(ctx: PipelineContext) -> dict[str, Any]:
    creative = ctx.out("creative")
    min_score = int(ctx.step_config.get("min_score", 18))
    max_score = int(ctx.step_config.get("max_score", 25))

    prompt = (
        f"{brand_summary(ctx.brand)}\n\n"
        f"Content to review (platform: {creative['platform']}):\n"
        f"SCRIPT:\n{creative['script']}\n\n"
        f"CAPTION:\n{creative['caption']}\n\n"
        f"{_RUBRIC} `notes` is one sentence on the weakest dimension."
    )
    res = claude_client.complete(
        prompt=prompt,
        system=_SYSTEM,
        max_tokens=700,
        json_schema=_SCHEMA,
        agent_type=ctx.agent_type,
        category="eval",
        tool_name="pipeline.eval_gate",
        brand_id=ctx.brand_id,
        run_id=ctx.run_id,
        budget_usd=ctx.budget_usd,
    )
    data = parse_step_json(res.text, res.stop_reason)
    total = int(data["total"])
    notes = str(data.get("notes", ""))
    passed = total >= min_score

    new_status = "IN_REVIEW" if passed else "FAILED"
    with connect() as conn:
        conn.execute(
            '''UPDATE "ContentPiece"
                  SET "evalScore" = %s, "evalNotes" = %s,
                      status = %s::"ContentStatus", "updatedAt" = now()
                WHERE id = %s''',
            (total, notes, new_status, creative["content_piece_id"]),
        )

    return {
        "total": total,
        "max_score": max_score,
        "min_score": min_score,
        "passed": passed,
        "scores": data.get("scores", {}),
        "notes": notes,
        "content_status": new_status,
        "cost_usd": res.cost_usd,
    }
