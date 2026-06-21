"""Execute a manifest's steps in order — the one orchestration path.

There is deliberately NO hardcoded step list here: the runner walks
`manifest.steps` and resolves each through the registry. Run lifecycle:

  RUNNING → (steps execute, cost accrues onto the AgentRun) → COMPLETED
                                                            ↘ FAILED (on error)

The eval gate is a step like any other; it marks the ContentPiece FAILED when
the score is under the floor (a non-publishable artifact), which the run records
in its outputData. A *pipeline* error (an exception in any step, incl. the
kill-switch tripping) marks the whole AgentRun FAILED.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from tools.pipeline import manifest as manifest_mod
from tools.pipeline.context import PipelineContext
from tools.pipeline.steps import resolve
from tools.utils.cost_logger import BudgetExceededError, get_run_cost
from tools.utils.db import connect
from tools.utils.ids import new_id

# Per-run kill-switch ceiling. A run that blows past this aborts mid-pipeline
# rather than spending unbounded. Override via env for cheaper/looser runs.
DEFAULT_RUN_BUDGET_USD = float(os.getenv("MAX_RUN_COST_USD", "2.0"))

_BRAND_FIELDS = (
    "name", "vertical", "language", "targetRegions", "voiceTone", "targetPersona",
)


@dataclass(frozen=True)
class RunResult:
    run_id: str
    status: str            # COMPLETED | FAILED
    cost_usd: float
    outputs: dict[str, Any]
    error: str | None = None


def _load_brand(brand_id: str) -> dict[str, Any]:
    cols = ", ".join(f'"{c}"' for c in _BRAND_FIELDS)
    with connect() as conn:
        row = conn.execute(
            f'SELECT {cols} FROM "Brand" WHERE id = %s', (brand_id,)
        ).fetchone()
    if row is None:
        raise ValueError(f"Brand {brand_id!r} not found")
    return dict(zip(_BRAND_FIELDS, row))


def create_run(brand_id: str, user_id: str, workflow_id: str, seed: str) -> str:
    """Insert a RUNNING AgentRun and return its id."""
    run_id = new_id("run")
    with connect() as conn:
        conn.execute(
            '''INSERT INTO "AgentRun"
                   (id, "brandId", "userId", "agentType", "workflowId", status,
                    "inputData", "updatedAt")
               VALUES (%s, %s, %s, %s::"AgentType", %s, %s::"RunStatus", %s::jsonb, now())''',
            (run_id, brand_id, user_id, "ORCHESTRATOR", workflow_id, "RUNNING",
             json.dumps({"seed": seed})),
        )
    return run_id


def _finalize(run_id: str, status: str, output: dict[str, Any], error: str | None) -> None:
    with connect() as conn:
        conn.execute(
            '''UPDATE "AgentRun"
                  SET status = %s::"RunStatus", "outputData" = %s::jsonb,
                      "errorMessage" = %s, "completedAt" = now(), "updatedAt" = now()
                WHERE id = %s''',
            (status, json.dumps(output), error, run_id),
        )


def run_pipeline(
    *,
    manifest_id: str = "content",
    brand_id: str,
    user_id: str,
    seed: str,
    budget_usd: float | None = None,
    run_id: str | None = None,
) -> RunResult:
    """Run a manifest end-to-end for one brand. Creates the AgentRun unless one
    is supplied (the durable-queue worker will pass a pre-created run_id)."""
    mf = manifest_mod.load_by_id(manifest_id)
    budget = budget_usd if budget_usd is not None else DEFAULT_RUN_BUDGET_USD
    brand = _load_brand(brand_id)
    if run_id is None:
        run_id = create_run(brand_id, user_id, mf.id, seed)

    ctx = PipelineContext(
        brand_id=brand_id, user_id=user_id, run_id=run_id, seed=seed,
        brand=brand, budget_usd=budget,
    )

    try:
        for step in mf.steps:
            ctx.step_name = step.name
            ctx.agent_type = step.agent_type
            ctx.step_config = step.config
            impl = resolve(step.step)
            ctx.outputs[step.name] = impl(ctx) or {}
    except BudgetExceededError as exc:
        cost = get_run_cost(run_id)
        _finalize(run_id, "FAILED", {"outputs": ctx.outputs}, str(exc))
        return RunResult(run_id, "FAILED", cost, ctx.outputs, error=str(exc))
    except Exception as exc:  # noqa: BLE001 — any step failure fails the run
        cost = get_run_cost(run_id)
        _finalize(run_id, "FAILED", {"outputs": ctx.outputs}, repr(exc))
        return RunResult(run_id, "FAILED", cost, ctx.outputs, error=repr(exc))

    cost = get_run_cost(run_id)
    output = {"outputs": ctx.outputs}
    _finalize(run_id, "COMPLETED", output, None)
    return RunResult(run_id, "COMPLETED", cost, ctx.outputs)
