"""The one typed enqueue helper + idempotent run provisioning.

`defer_pipeline()` durably enqueues a content run and returns its `AgentRun` id.
Ordering matters for the "no orphaned RUNNING" guarantee:

  1. Procrastinate commits the job row (durable) and returns a job id.
  2. We derive a deterministic `run_id` from that job id and upsert the AgentRun.

Because the run_id is derived from the job id and the upsert is idempotent, the
worker re-derives the exact same run_id and ensures the row exists before running
(see tools/runtime/tasks.py). So a crash between steps 1 and 2 cannot orphan a
run — the worker creates it. A retry after a mid-run crash reuses the same run_id.
"""
from __future__ import annotations

import json

from tools.runtime.aio import run_async
from tools.runtime.app import app
from tools.utils.db import connect


def run_id_for_job(job_id: int) -> str:
    """Deterministic AgentRun id for a Procrastinate job (stable across retries)."""
    return f"runj{int(job_id)}"


def ensure_run(
    run_id: str,
    *,
    brand_id: str,
    user_id: str,
    workflow_id: str,
    seed: str,
) -> None:
    """Idempotently create the AgentRun row (RUNNING). Safe to call repeatedly —
    the deferrer and the worker both call it; ON CONFLICT DO NOTHING dedupes."""
    with connect() as conn:
        conn.execute(
            '''INSERT INTO "AgentRun"
                   (id, "brandId", "userId", "agentType", "workflowId", status,
                    "inputData", "updatedAt")
               VALUES (%s, %s, %s, %s::"AgentType", %s, %s::"RunStatus", %s::jsonb, now())
               ON CONFLICT (id) DO NOTHING''',
            (run_id, brand_id, user_id, "ORCHESTRATOR", workflow_id, "RUNNING",
             json.dumps({"seed": seed})),
        )


def defer_pipeline(
    *,
    manifest_id: str = "content",
    brand_id: str,
    user_id: str,
    seed: str,
    budget_usd: float | None = None,
) -> tuple[str, int]:
    """Enqueue a content-pipeline run. Returns (run_id, job_id).

    The run executes on the worker, not here — this returns as soon as the job is
    durably committed.
    """

    async def _defer() -> int:
        from tools.runtime.tasks import run_pipeline_task

        async with app.open_async():
            return await run_pipeline_task.defer_async(
                manifest_id=manifest_id,
                brand_id=brand_id,
                user_id=user_id,
                seed=seed,
                budget_usd=budget_usd,
            )

    job_id = run_async(_defer())
    run_id = run_id_for_job(job_id)
    ensure_run(run_id, brand_id=brand_id, user_id=user_id, workflow_id=manifest_id, seed=seed)
    return run_id, job_id
