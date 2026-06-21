"""Prove the LLM gateway + cost ledger end-to-end (porting step 3).

Per CLAUDE.md §3 "Verify, don't assume": this makes REAL (tiny) Claude calls and
shows that the trust fixes actually hold:

  1. A call through the gateway writes a non-zero `CostLog` row the dashboard
     reads.
  2. Per-call spend accumulates onto a real `AgentRun` (costUsd / tokensUsed).
  3. The pre-call kill-switch aborts a call once the run is over budget — a real
     abort, not a print().

It provisions a disposable User + Brand + AgentRun, runs the proof, prints the
ledger rows, then deletes everything it created (idempotent; leaves no residue).
Cost is fractions of a cent.

Run:  .venv/Scripts/python scripts/prove-gateway.py
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

# Allow `python scripts/prove-gateway.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from tools.utils import claude_client, cost_logger  # noqa: E402
from tools.utils.db import connect  # noqa: E402

USER_ID = str(uuid.uuid4())
USER_EMAIL = f"gateway-proof+{USER_ID[:8]}@example.com"
BRAND_ID = "cproof" + uuid.uuid4().hex[:18]
BRAND_SLUG = f"gateway-proof-{uuid.uuid4().hex[:8]}"
RUN_ID = "rproof" + uuid.uuid4().hex[:18]
# Each proof call costs ~$0.000185 (17 in + 4 out on Opus 4.8). A budget between
# the 1-call and 2-call totals means call 3's pre-check trips the kill-switch.
BUDGET_USD = 0.0003


def seed() -> None:
    with connect(autocommit=False) as conn:
        with conn.transaction():
            conn.execute(
                'INSERT INTO "User" (id, email, name, "updatedAt") VALUES (%s, %s, %s, now())',
                (USER_ID, USER_EMAIL, "Gateway Proof"),
            )
            conn.execute(
                '''INSERT INTO "Brand" (id, "userId", name, slug, vertical, "updatedAt")
                   VALUES (%s, %s, %s, %s, %s, now())''',
                (BRAND_ID, USER_ID, "Gateway Proof Brand", BRAND_SLUG, "test"),
            )
            conn.execute(
                '''INSERT INTO "AgentRun"
                       (id, "brandId", "userId", "agentType", "workflowId", "inputData", "updatedAt")
                   VALUES (%s, %s, %s, %s::"AgentType", %s, %s::jsonb, now())''',
                (RUN_ID, BRAND_ID, USER_ID, "ORCHESTRATOR", "prove-gateway", "{}"),
            )


def teardown() -> None:
    # Cascade from User removes Brand → AgentRun; CostLog.brandId is SetNull, so
    # delete its rows explicitly first.
    with connect(autocommit=False) as conn:
        with conn.transaction():
            conn.execute('DELETE FROM "CostLog" WHERE "brandId" = %s', (BRAND_ID,))
            conn.execute('DELETE FROM "User" WHERE id = %s', (USER_ID,))


def main() -> int:
    print("== seeding disposable User + Brand + AgentRun ==")
    seed()
    try:
        print(f"  run_id   : {RUN_ID}")
        print(f"  budget   : ${BUDGET_USD:.4f}")
        print()

        print("== call 1 (through the gateway) ==")
        r1 = claude_client.complete(
            prompt="Reply with the single word: pong.",
            max_tokens=16,
            agent_type="ORCHESTRATOR",
            category="proof",
            tool_name="prove-gateway",
            brand_id=BRAND_ID,
            run_id=RUN_ID,
            budget_usd=BUDGET_USD,
        )
        print(f"  model      : {r1.model}")
        print(f"  reply      : {r1.text.strip()!r}")
        print(f"  usage      : {r1.usage}")
        print(f"  call cost  : ${r1.cost_usd:.6f}")
        print(f"  run total  : ${r1.run_total_usd:.6f}")
        assert r1.cost_usd > 0, "FAIL: call cost is zero — ledger would be fiction"
        print()

        print("== call 2 (accumulates onto the same run) ==")
        r2 = claude_client.complete(
            prompt="Reply with the single word: pong.",
            max_tokens=16,
            agent_type="ORCHESTRATOR",
            category="proof",
            tool_name="prove-gateway",
            brand_id=BRAND_ID,
            run_id=RUN_ID,
            budget_usd=BUDGET_USD,
        )
        print(f"  call cost  : ${r2.cost_usd:.6f}")
        print(f"  run total  : ${r2.run_total_usd:.6f}")
        assert r2.run_total_usd > r1.run_total_usd, "FAIL: run total did not accumulate"
        print()

        print("== ledger rows the dashboard reads (CostLog) ==")
        with connect() as conn:
            rows = conn.execute(
                '''SELECT model, "tokensIn", "tokensOut", "costUsd", category
                     FROM "CostLog" WHERE "brandId" = %s ORDER BY "createdAt"''',
                (BRAND_ID,),
            ).fetchall()
            for model, tin, tout, cost, cat in rows:
                print(f"  {model}  in={tin} out={tout}  ${float(cost):.6f}  [{cat}]")
            run_cost = conn.execute(
                'SELECT "costUsd", "tokensUsed" FROM "AgentRun" WHERE id = %s', (RUN_ID,)
            ).fetchone()
        print(f"  AgentRun.costUsd = ${float(run_cost[0]):.6f}  tokensUsed = {run_cost[1]}")
        assert len(rows) == 2, f"FAIL: expected 2 CostLog rows, found {len(rows)}"
        print()

        print(f"== kill-switch (run total ${r2.run_total_usd:.6f} now over the ${BUDGET_USD:.4f} budget) ==")
        try:
            claude_client.complete(
                prompt="This call must never reach Anthropic.",
                max_tokens=16,
                brand_id=BRAND_ID,
                run_id=RUN_ID,
                budget_usd=BUDGET_USD,
            )
            print("  FAIL: kill-switch did NOT abort the call")
            return 1
        except cost_logger.BudgetExceededError as exc:
            print(f"  aborted as expected: {exc}")
            # Prove no 3rd row was written — the abort happened pre-call.
            with connect() as conn:
                n = conn.execute(
                    'SELECT count(*) FROM "CostLog" WHERE "brandId" = %s', (BRAND_ID,)
                ).fetchone()[0]
            assert n == 2, f"FAIL: kill-switch leaked a call — {n} CostLog rows"
            print(f"  CostLog row count still {n} (no spend after the switch tripped)")
        print()
        print("OK — gateway logs real cost, accumulates onto the run, and the kill-switch is real.")
        return 0
    finally:
        print("\n== tearing down disposable rows ==")
        teardown()
        print("  done")


if __name__ == "__main__":
    raise SystemExit(main())
