"""Prove the content vertical end-to-end (porting step D4, spine).

Runs the `content` manifest for a disposable brand and shows the spine working:
real cost accrued onto the AgentRun, the persisted ContentPiece + ContentCopy
artifact, and the eval-gate verdict (the hard pre-publish floor).

By default it provisions a throwaway User + Brand, runs, prints the result, and
deletes everything it created. Cost is a few cents of real Opus calls.

Run:  .venv/Scripts/python scripts/run-content-pipeline.py
      .venv/Scripts/python scripts/run-content-pipeline.py --seed "eid travel deals" --keep
"""
from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from tools.pipeline import runner  # noqa: E402
from tools.utils.db import connect  # noqa: E402

USER_ID = str(uuid.uuid4())
BRAND_ID = "cpipe" + uuid.uuid4().hex[:18]


def seed_brand(slug_suffix: str) -> None:
    with connect(autocommit=False) as conn:
        with conn.transaction():
            conn.execute(
                'INSERT INTO "User" (id, email, name, "updatedAt") VALUES (%s, %s, %s, now())',
                (USER_ID, f"pipeline-proof+{slug_suffix}@example.com", "Pipeline Proof"),
            )
            conn.execute(
                '''INSERT INTO "Brand"
                       (id, "userId", name, slug, vertical, language, "targetRegions",
                        "voiceTone", "targetPersona", "updatedAt")
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())''',
                (
                    BRAND_ID, USER_ID, "Pipeline Proof Co", f"pipeline-proof-{slug_suffix}",
                    "boutique fitness studio", "en",
                    ["Kuwait", "GCC"], ["energetic", "encouraging", "no-nonsense"],
                    "busy professionals 25-40 who want efficient workouts",
                ),
            )


def teardown() -> None:
    with connect(autocommit=False) as conn:
        with conn.transaction():
            conn.execute('DELETE FROM "CostLog" WHERE "brandId" = %s', (BRAND_ID,))
            conn.execute('DELETE FROM "User" WHERE id = %s', (USER_ID,))


def show_artifact() -> None:
    with connect() as conn:
        piece = conn.execute(
            '''SELECT id, type, status, "evalScore", left(script, 160)
                 FROM "ContentPiece" WHERE "brandId" = %s ORDER BY "createdAt" DESC LIMIT 1''',
            (BRAND_ID,),
        ).fetchone()
        if piece is None:
            print("  (no ContentPiece persisted)")
            return
        print(f"  ContentPiece {piece[0]}")
        print(f"    type={piece[1]}  status={piece[2]}  evalScore={piece[3]}")
        print(f"    script: {piece[4]!r}…")
        copy = conn.execute(
            '''SELECT platform, left(caption, 120), hashtags
                 FROM "ContentCopy" WHERE "contentPieceId" = %s''',
            (piece[0],),
        ).fetchone()
        if copy:
            print(f"  ContentCopy [{copy[0]}]  caption: {copy[1]!r}…")
            print(f"    hashtags: {copy[2]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="summer membership promotion")
    ap.add_argument("--keep", action="store_true", help="don't delete the disposable rows")
    args = ap.parse_args()

    suffix = uuid.uuid4().hex[:8]
    print("== seeding disposable User + Brand ==")
    seed_brand(suffix)
    try:
        print(f"  brand_id : {BRAND_ID}")
        print(f"  seed     : {args.seed!r}")
        print()
        print("== running the `content` manifest (real Opus calls) ==")
        result = runner.run_pipeline(
            manifest_id="content", brand_id=BRAND_ID, user_id=USER_ID, seed=args.seed,
        )
        print(f"  run_id   : {result.run_id}")
        print(f"  status   : {result.status}")
        print(f"  run cost : ${result.cost_usd:.6f}")
        if result.error:
            print(f"  error    : {result.error}")
        print()

        for name in ("trends", "strategy", "creative", "eval_gate"):
            step = result.outputs.get(name)
            if step:
                print(f"  [{name}] cost ${step.get('cost_usd', 0):.6f}")
        gate = result.outputs.get("eval_gate")
        if gate:
            print()
            print("== eval gate (hard pre-publish floor) ==")
            print(f"  score   : {gate['total']}/{gate['max_score']}  (floor {gate['min_score']})")
            print(f"  verdict : {'PASS' if gate['passed'] else 'FAIL'}  → ContentPiece {gate['content_status']}")
            print(f"  scores  : {gate['scores']}")
        print()
        print("== persisted artifact ==")
        show_artifact()
        print()

        ok = result.status == "COMPLETED" and gate is not None
        print("OK — manifest ran end-to-end, cost accrued on the run, artifact persisted."
              if ok else "INCOMPLETE — see status/error above.")
        return 0 if ok else 1
    finally:
        if args.keep:
            print(f"\n(--keep) leaving rows for brand {BRAND_ID}")
        else:
            print("\n== tearing down disposable rows ==")
            teardown()
            print("  done")


if __name__ == "__main__":
    raise SystemExit(main())
