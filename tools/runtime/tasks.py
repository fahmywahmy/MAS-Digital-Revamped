"""Durable tasks. The worker imports this module (via app.import_paths) so the
task registry is populated in the worker process.

The pipeline task is idempotent on its derived run_id: on a retry after a crash it
reuses the same AgentRun rather than spawning a duplicate.
"""
from __future__ import annotations

from typing import Any

from tools.runtime.app import app
from tools.runtime.defer import ensure_run, run_id_for_job


@app.task(name="run_pipeline", queue="pipeline", pass_context=True)
def run_pipeline_task(
    context,
    *,
    manifest_id: str,
    brand_id: str,
    user_id: str,
    seed: str,
    budget_usd: float | None = None,
) -> dict[str, Any]:
    # Imported lazily so importing this module (e.g. for the schema preview)
    # doesn't pull in the whole pipeline/LLM stack.
    from tools.pipeline.runner import run_pipeline

    run_id = run_id_for_job(context.job.id)
    # Guarantee the run row exists even if the deferrer crashed before creating it.
    ensure_run(run_id, brand_id=brand_id, user_id=user_id, workflow_id=manifest_id, seed=seed)

    result = run_pipeline(
        manifest_id=manifest_id,
        brand_id=brand_id,
        user_id=user_id,
        seed=seed,
        run_id=run_id,
        budget_usd=budget_usd,
    )
    return {"run_id": result.run_id, "status": result.status, "cost_usd": result.cost_usd}
