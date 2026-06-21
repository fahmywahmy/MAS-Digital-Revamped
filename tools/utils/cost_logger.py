"""The one cost ledger (CLAUDE.md §2.1, §2.2; fix-on-port §C1).

The legacy system's headline budget control was fiction: the table the UI read
was never written. Here the ledger is wired correctly and verifiably:

  1. Every gateway call writes a `CostLog` row (DB-primary) that `/api/costs`
     reads.
  2. Real per-call spend accumulates onto the owning `AgentRun`
     (`costUsd` / `tokensUsed`).
  3. A real pre-call kill-switch (`check_budget`) raises and aborts a run that
     is already over budget — not a `print()`.

This module is the ONLY writer of CostLog and of AgentRun spend.
"""
from __future__ import annotations

from dataclasses import dataclass

from tools.utils.db import connect
from tools.utils.ids import new_id
from tools.utils.registry import cost_usd

VALID_AGENT_TYPES = frozenset(
    {"ORCHESTRATOR", "RESEARCH_STRATEGY", "CREATIVE", "ANALYTICS_SAFETY"}
)


class BudgetExceededError(RuntimeError):
    """A run is over its budget. Raised pre-call so no further spend occurs."""

    def __init__(self, run_id: str, spent: float, budget: float):
        self.run_id = run_id
        self.spent = spent
        self.budget = budget
        super().__init__(
            f"Run {run_id} kill-switch tripped: spent ${spent:.4f} ≥ budget ${budget:.4f}. "
            f"Aborting before the next call."
        )


@dataclass(frozen=True)
class LoggedCost:
    cost_log_id: str
    cost_usd: float
    run_total_usd: float | None  # accumulated AgentRun total, or None when run_id absent


def _gen_id() -> str:
    # CostLog.id is an opaque String @id, never used as a foreign key.
    return new_id("c")


def get_run_cost(run_id: str) -> float:
    """Current accumulated spend on an AgentRun (USD)."""
    with connect() as conn:
        row = conn.execute('SELECT "costUsd" FROM "AgentRun" WHERE id = %s', (run_id,)).fetchone()
    if row is None:
        raise ValueError(f"AgentRun {run_id!r} not found")
    return float(row[0])


def check_budget(run_id: str, budget_usd: float) -> float:
    """Pre-call kill-switch. Raise BudgetExceededError if the run is already at
    or over budget. Returns current spend when within budget."""
    spent = get_run_cost(run_id)
    if spent >= budget_usd:
        raise BudgetExceededError(run_id, spent, budget_usd)
    return spent


def record_call(
    *,
    model: str,
    tokens_in: int,
    tokens_out: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    agent_type: str,
    category: str,
    tool_name: str | None = None,
    brand_id: str | None = None,
    run_id: str | None = None,
) -> LoggedCost:
    """Price one call, write its CostLog row, and accumulate onto the AgentRun.

    The write and the run-accumulation happen in one transaction so the ledger
    and the run total can never drift apart.
    """
    if agent_type not in VALID_AGENT_TYPES:
        raise ValueError(f"agent_type {agent_type!r} not in {sorted(VALID_AGENT_TYPES)}")

    cost = cost_usd(
        model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cache_read_tokens=cache_read_tokens,
        cache_creation_tokens=cache_creation_tokens,
    )
    cost_log_id = _gen_id()
    tokens_total = tokens_in + tokens_out + cache_read_tokens + cache_creation_tokens

    with connect(autocommit=False) as conn:
        with conn.transaction():
            conn.execute(
                '''
                INSERT INTO "CostLog"
                    (id, "brandId", "agentType", model, "tokensIn", "tokensOut",
                     "cacheReadTokens", "cacheCreationTokens", "costUsd", category, "toolName")
                VALUES (%s, %s, %s::"AgentType", %s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                (
                    cost_log_id, brand_id, agent_type, model,
                    tokens_in, tokens_out, cache_read_tokens, cache_creation_tokens,
                    cost, category, tool_name,
                ),
            )
            run_total: float | None = None
            if run_id is not None:
                row = conn.execute(
                    '''
                    UPDATE "AgentRun"
                       SET "tokensUsed" = "tokensUsed" + %s,
                           "costUsd"    = "costUsd" + %s,
                           "updatedAt"  = now()
                     WHERE id = %s
                    RETURNING "costUsd"
                    ''',
                    (tokens_total, cost, run_id),
                ).fetchone()
                if row is None:
                    raise ValueError(f"AgentRun {run_id!r} not found — cannot accumulate cost")
                run_total = float(row[0])

    return LoggedCost(cost_log_id=cost_log_id, cost_usd=cost, run_total_usd=run_total)
