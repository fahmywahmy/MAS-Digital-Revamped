"""Self-healing on worker startup — the heart of "no orphaned RUNNING".

When a worker dies mid-job, its job stays `doing` (locked to the now-dead worker)
and `fetch_job` will never pick it up — it would sit forever, and its AgentRun
would be stuck RUNNING. On startup a worker calls `recover_stalled()`, which finds
jobs whose worker's heartbeat has gone stale, re-queues them (`retry_job` → `todo`),
then prunes the dead worker rows. The fresh worker then fetches and re-runs them;
the pipeline task is idempotent on its derived run_id, so the same AgentRun finishes.

Order matters: re-queue the stalled jobs BEFORE pruning their workers — pruning
nulls `worker_id` (ON DELETE SET NULL) and would hide them from `get_stalled_jobs`.

The threshold must exceed the heartbeat interval so a momentarily-slow live worker
isn't reclaimed (double-execution). Default 30s; override via MAS_RECOVER_THRESHOLD_S
(the restart proof sets it low for a fast, deterministic run).

Procrastinate's JobManager is async-native, so recovery runs on the async connector
via asyncio and is exposed through a small sync wrapper for the worker entrypoint.
"""
from __future__ import annotations

import os

from tools.runtime.aio import run_async
from tools.runtime.app import app

DEFAULT_THRESHOLD_S = float(os.getenv("MAS_RECOVER_THRESHOLD_S", "30"))


async def _recover_async(threshold_s: float) -> dict:
    async with app.open_async():
        jm = app.job_manager
        stalled = list(await jm.get_stalled_jobs(seconds_since_heartbeat=threshold_s))
        for job in stalled:
            await jm.retry_job(job)
        pruned = await jm.prune_stalled_workers(threshold_s)
    return {
        "recovered": len(stalled),
        "pruned_workers": len(pruned),
        "job_ids": [j.id for j in stalled],
    }


def recover_stalled(threshold_s: float | None = None) -> dict:
    t = DEFAULT_THRESHOLD_S if threshold_s is None else threshold_s
    return run_async(_recover_async(t))
