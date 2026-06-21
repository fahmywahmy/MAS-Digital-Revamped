"""Durable runtime — the queue that makes long content runs survive a restart.

Built on Procrastinate (Postgres-backed) in a DEDICATED `procrastinate` schema,
isolated from the Prisma-owned `public` tables. The webapp/control plane enqueues
a pipeline run via the one typed `defer_pipeline()` helper; a long-lived worker
consumes it. A worker crash mid-run does not orphan the AgentRun: Procrastinate's
stalled-job recovery re-queues the job, and the run finalizes on completion.

See docs/MASTERPLAN.md §P1. The schema is applied separately (NOT via the Prisma
chain) and is gated on operator approval — see scripts/show-procrastinate-schema.py.
"""
