"""Step 4 — eval gate. The hard pre-publish floor.

Scores the content with the calibrated judge (judge ≠ generator, locked rubric
bands, deterministic guards — see tools/pipeline/eval_rubric.py). A pass marks the
ContentPiece publishable (IN_REVIEW); a sub-floor score OR a hard guard failure
marks it FAILED.

This is a quality floor, not a system error: failing the artifact does not fail
the *run* (the pipeline executed) — the run records the verdict in its outputData.
"""
from __future__ import annotations

from typing import Any

from tools.pipeline.context import PipelineContext
from tools.pipeline.eval_rubric import DEFAULT_JUDGE_MODEL, judge_content
from tools.utils.db import connect


def run(ctx: PipelineContext) -> dict[str, Any]:
    creative = ctx.out("creative")
    min_score = int(ctx.step_config.get("min_score", 18))
    max_score = int(ctx.step_config.get("max_score", 25))
    judge_model = ctx.step_config.get("judge_model", DEFAULT_JUDGE_MODEL)

    verdict = judge_content(
        brand=ctx.brand,
        script=creative["script"],
        caption=creative["caption"],
        platform=creative["platform"],
        min_score=min_score,
        max_score=max_score,
        judge_model=judge_model,
        brand_id=ctx.brand_id,
        run_id=ctx.run_id,
        budget_usd=ctx.budget_usd,
    )

    # Eval notes capture both the judge's note and any hard guard failures, so the
    # operator sees *why* a piece was blocked, not just the number.
    note_parts = [verdict["notes"]]
    if verdict["hard_failed"]:
        blocked = "; ".join(
            f"{g['name']} ({g['detail']})" for g in verdict["guard_failures"] if g["hard"]
        )
        note_parts.append(f"BLOCKED by guards: {blocked}")
    notes = " — ".join(p for p in note_parts if p)

    new_status = "IN_REVIEW" if verdict["passed"] else "FAILED"
    with connect() as conn:
        conn.execute(
            '''UPDATE "ContentPiece"
                  SET "evalScore" = %s, "evalNotes" = %s,
                      status = %s::"ContentStatus", "updatedAt" = now()
                WHERE id = %s''',
            (verdict["total"], notes, new_status, creative["content_piece_id"]),
        )

    return {
        **verdict,
        "content_status": new_status,
        "notes": notes,
    }
