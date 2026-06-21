"""Restart-survival proof (MASTERPLAN P1) — the durable-runtime guarantee.

Proves a content run survives a worker crash: it is NOT orphaned as RUNNING, and a
restarted worker resumes and completes it. Sequence:

  1. Seed a disposable brand + user; defer a real content run (AgentRun = RUNNING).
  2. Start worker A; wait until it's actually executing the run (job `doing` + the
     first artifact persisted).
  3. KILL worker A (hard, mid-run) — simulating a crash. Assert the run is still
     RUNNING (not orphaned, not falsely COMPLETED).
  4. Start worker B. Its startup self-heal re-queues the orphaned job; it resumes
     and runs the pipeline to completion. Assert AgentRun → COMPLETED.

Makes real Opus calls (the run executes ~1.x times due to at-least-once retry,
~$0.10-0.15). Cleans up everything it created.

Run:  .venv/Scripts/python scripts/prove-restart-survival.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from tools.runtime.defer import defer_pipeline  # noqa: E402
from tools.utils.db import connect  # noqa: E402

USER_ID = str(uuid.uuid4())
BRAND_ID = "crestart" + uuid.uuid4().hex[:16]
SLUG = f"restart-proof-{uuid.uuid4().hex[:8]}"
TMP = REPO_ROOT / ".tmp"
RECOVER_THRESHOLD_S = 3


def seed() -> None:
    with connect(autocommit=False) as conn:
        with conn.transaction():
            conn.execute(
                'INSERT INTO "User" (id, email, name, "updatedAt") VALUES (%s,%s,%s,now())',
                (USER_ID, f"restart-proof+{SLUG}@example.com", "Restart Proof"),
            )
            conn.execute(
                '''INSERT INTO "Brand"
                       (id,"userId",name,slug,vertical,language,"targetRegions",
                        "voiceTone","targetPersona","updatedAt")
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,now())''',
                (BRAND_ID, USER_ID, "Restart Proof Co", SLUG, "travel agency", "en",
                 ["Kuwait"], ["warm", "efficient"], "Kuwaiti families planning summer trips"),
            )


def teardown(procs: list[subprocess.Popen]) -> None:
    for p in procs:
        if p and p.poll() is None:
            p.kill()
    with connect(autocommit=False) as conn:
        with conn.transaction():
            conn.execute('DELETE FROM procrastinate.procrastinate_jobs '
                         "WHERE args->>'brand_id' = %s", (BRAND_ID,))
            conn.execute('DELETE FROM "CostLog" WHERE "brandId" = %s', (BRAND_ID,))
            conn.execute('DELETE FROM "User" WHERE id = %s', (USER_ID,))


def run_status(run_id: str) -> str | None:
    with connect() as conn:
        row = conn.execute('SELECT status FROM "AgentRun" WHERE id = %s', (run_id,)).fetchone()
    return row[0] if row else None


def job_status() -> str | None:
    with connect() as conn:
        row = conn.execute("SELECT status::text FROM procrastinate.procrastinate_jobs "
                           "WHERE args->>'brand_id' = %s ORDER BY id DESC LIMIT 1",
                           (BRAND_ID,)).fetchone()
    return row[0] if row else None


def first_artifact_exists() -> bool:
    with connect() as conn:
        n = conn.execute('SELECT count(*) FROM "TrendScan" WHERE "brandId" = %s',
                         (BRAND_ID,)).fetchone()[0]
    return n > 0


def spawn_worker(log_name: str) -> subprocess.Popen:
    TMP.mkdir(exist_ok=True)
    env = dict(os.environ, MAS_RECOVER_THRESHOLD_S=str(RECOVER_THRESHOLD_S))
    log = open(TMP / log_name, "w", encoding="utf-8", errors="replace")
    return subprocess.Popen(
        [sys.executable, "-m", "tools.runtime.worker"],
        cwd=str(REPO_ROOT), env=env, stdout=log, stderr=subprocess.STDOUT,
    )


def wait_until(predicate, timeout: float, interval: float = 1.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


def main() -> int:
    print("== Restart-survival proof ==")
    seed()
    procs: list[subprocess.Popen] = []
    try:
        run_id, job_id = defer_pipeline(
            manifest_id="content", brand_id=BRAND_ID, user_id=USER_ID,
            seed="summer Europe escape", budget_usd=2.0,
        )
        print(f"  deferred: run_id={run_id} job_id={job_id}")
        print(f"  AgentRun status at defer: {run_status(run_id)}")
        assert run_status(run_id) == "RUNNING"

        print("\n-- start worker A, wait until it's executing the run --")
        worker_a = spawn_worker("workerA.log")
        procs.append(worker_a)
        started = wait_until(
            lambda: job_status() == "doing" and first_artifact_exists(), timeout=90
        )
        if not started:
            print("  FAIL: worker A did not start executing the run in time")
            print((TMP / "workerA.log").read_text(encoding="utf-8", errors="replace")[-800:])
            return 1
        print(f"  worker A is mid-run (job={job_status()}, first artifact persisted)")

        print("\n-- KILL worker A (simulated crash) --")
        worker_a.kill()
        worker_a.wait(timeout=10)
        time.sleep(RECOVER_THRESHOLD_S + 2)  # let the dead worker's heartbeat go stale
        st = run_status(run_id)
        print(f"  after crash: AgentRun status = {st}, job status = {job_status()}")
        assert st == "RUNNING", f"FAIL: run should still be RUNNING (orphan check), got {st}"
        assert st != "COMPLETED", "FAIL: run cannot be COMPLETED — worker died mid-run"
        print("  OK: run is neither orphaned-FAILED nor falsely COMPLETED — it is RUNNING")

        print("\n-- restart: start worker B (self-heals + resumes) --")
        worker_b = spawn_worker("workerB.log")
        procs.append(worker_b)
        done = wait_until(lambda: run_status(run_id) == "COMPLETED", timeout=150)
        log_b = (TMP / "workerB.log").read_text(encoding="utf-8", errors="replace")
        for line in log_b.splitlines():
            if "recovered" in line or "starting" in line:
                print(f"  [B] {line.strip()}")
        if not done:
            print(f"  FAIL: run did not complete after restart (status={run_status(run_id)})")
            print(log_b[-800:])
            return 1

        with connect() as conn:
            cost = conn.execute('SELECT "costUsd" FROM "AgentRun" WHERE id=%s',
                                (run_id,)).fetchone()[0]
        print(f"  OK: AgentRun COMPLETED after restart. Real cost on the run: ${float(cost):.4f}")
        print("\nOK — a content run survived a worker crash: not orphaned, resumed, completed.")
        return 0
    finally:
        print("\n== teardown ==")
        teardown(procs)
        print("  done")


if __name__ == "__main__":
    raise SystemExit(main())
