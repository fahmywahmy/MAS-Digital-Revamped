"""The one Postgres connection helper for the toolchain.

Thin wrapper over psycopg3 + the credential door. Tables are PascalCase
(Prisma), so callers quote identifiers: `'CostLog'`, `'AgentRun'`.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg

from tools.utils.config import database_dsn


@contextmanager
def connect(*, autocommit: bool = True, connect_timeout: int = 20) -> Iterator[psycopg.Connection]:
    """Open a short-lived connection to the app database.

    autocommit=True suits the ledger's single-row writes; pass autocommit=False
    when a caller needs a multi-statement transaction.
    """
    conn = psycopg.connect(database_dsn(), autocommit=autocommit, connect_timeout=connect_timeout)
    try:
        yield conn
    finally:
        conn.close()
