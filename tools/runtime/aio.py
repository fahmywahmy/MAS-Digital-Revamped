"""Run an async coroutine from sync code, with a psycopg-compatible event loop.

psycopg's async mode cannot run on Windows' default ProactorEventLoop — it requires
a SelectorEventLoop. Every sync entry point that drives the async Procrastinate /
psycopg stack (defer, recovery, worker) goes through `run_async` so the right loop
is selected on Windows and the default is used elsewhere.
"""
from __future__ import annotations

import asyncio
import sys
from typing import Awaitable, TypeVar

_T = TypeVar("_T")


def run_async(coro: Awaitable[_T]) -> _T:
    if sys.platform == "win32":
        # Idempotent; selects a SelectorEventLoop for psycopg async compatibility.
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(coro)  # type: ignore[arg-type]
