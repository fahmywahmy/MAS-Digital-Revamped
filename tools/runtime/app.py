"""The one Procrastinate App + its dedicated-schema connector config.

`app` is the canonical instance that owns the task registry and uses a SYNC
connector — so `defer_pipeline()` and scripts can enqueue from ordinary sync code.
`worker_app()` returns the same app with an ASYNC connector (LISTEN/NOTIFY) for the
long-running worker process, via `replace_connector` (shared task registry).

Both connect with `search_path=procrastinate`, so every Procrastinate object
resolves inside the dedicated schema and nothing leaks into the Prisma-owned
`public` tables. The pipeline's own DB writes use `tools.utils.db.connect()`
(default `public` search_path) — separate connections, separate schemas.
"""
from __future__ import annotations

from procrastinate import App, PsycopgConnector, SyncPsycopgConnector

from tools.utils.config import database_dsn

SCHEMA_NAME = "procrastinate"
# Keep the pool tiny — Supabase direct connections (5432) are a scarce resource
# on the free tier (~60 total), and this is a 1-3 operator shop.
_MIN_SIZE = 1
_MAX_SIZE = 4


def _connector_kwargs() -> dict:
    return {
        "conninfo": database_dsn(),
        # libpq options: pin the search_path so unqualified procrastinate_* names
        # resolve inside the dedicated schema on every connection.
        "kwargs": {"options": f"-c search_path={SCHEMA_NAME}"},
        "min_size": _MIN_SIZE,
        "max_size": _MAX_SIZE,
    }


# Canonical app — sync connector, owns the task registry (see tools/runtime/tasks.py).
app = App(
    connector=SyncPsycopgConnector(**_connector_kwargs()),
    import_paths=["tools.runtime.tasks"],
)


def worker_app() -> App:
    """The same app with an async connector, for the long-running worker.

    Async gives real `pg_notify` LISTEN/NOTIFY wakeups; on a transaction-pooled
    connection that can't LISTEN, Procrastinate degrades to polling automatically.
    """
    return app.replace_connector(PsycopgConnector(**_connector_kwargs()))
