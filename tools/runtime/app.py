"""The one Procrastinate App + its dedicated-schema connector config.

Procrastinate is async-native, so `app` uses the async `PsycopgConnector` (real
`pg_notify` LISTEN/NOTIFY wakeups; on a transaction-pooled connection that can't
LISTEN it degrades to polling automatically). Sync entry points — `defer_pipeline()`
and the worker `main()` — wrap the async API with `asyncio.run`, so callers stay
ordinary sync code without juggling two connectors.

The connector pins `search_path=procrastinate`, so every object resolves inside the
dedicated schema; combined with the function-level `search_path` hardening in the
install SQL, nothing leaks into the Prisma-owned `public` tables. The pipeline's own
DB writes use `tools.utils.db.connect()` (default `public`) — separate connections.
"""
from __future__ import annotations

from procrastinate import App, PsycopgConnector

from tools.utils.config import database_dsn

SCHEMA_NAME = "procrastinate"
# Keep the pool tiny — Supabase direct connections (5432) are scarce on the free
# tier (~60 total), and this is a 1-3 operator shop.
_MIN_SIZE = 1
_MAX_SIZE = 4


def _connector_kwargs() -> dict:
    return {
        "conninfo": database_dsn(),
        # libpq options: pin search_path so unqualified procrastinate_* names resolve
        # inside the dedicated schema on every connection.
        "kwargs": {"options": f"-c search_path={SCHEMA_NAME}"},
        "min_size": _MIN_SIZE,
        "max_size": _MAX_SIZE,
    }


app = App(
    connector=PsycopgConnector(**_connector_kwargs()),
    import_paths=["tools.runtime.tasks"],
)
