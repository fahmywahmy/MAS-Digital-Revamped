"""Eval-gate discrimination + FAIL-path proof (MASTERPLAN P1).

Exercises the calibrated judge on reference artifacts to prove the gate actually
gates — the thing the P0 run (which scored a suspicious 25/25) never demonstrated:

  - a deliberately WEAK artifact is BLOCKED (< floor)               → FAIL path
  - a compliance-violating artifact is HARD-BLOCKED by guards       → deterministic
  - a STRONG artifact scores materially higher than the weak one    → discrimination

Makes 3 real judge calls (Sonnet 4.6, ~cents); logged to CostLog (category 'eval',
null brand) and cleaned up at the end. No pipeline/DB run involved.

Run:  .venv/Scripts/python scripts/check-eval-gate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from tools.pipeline.eval_rubric import judge_content  # noqa: E402
from tools.utils.db import connect  # noqa: E402

BRAND = {
    "name": "Demo Travel Co",
    "vertical": "travel agency",
    "language": "en",
    "targetRegions": ["Kuwait", "GCC"],
    "voiceTone": ["warm", "aspirational", "efficient"],
    "targetPersona": "Kuwaiti families and young professionals planning summer trips",
}

STRONG = dict(
    label="STRONG",
    script=("POV: it's 48°C in Kuwait and you just booked 10 days across the Swiss Alps. "
            "Cool mountain mornings, lakeside walks, zero stress — we handle the flights, "
            "the hotels, and the visa. Your summer escape starts with one message."),
    caption=("Trade the heat for the Alps this summer. Flights, hotels, and visa — fully "
             "handled by our team. Message us on WhatsApp and we'll send your Switzerland "
             "itinerary today."),
    platform="INSTAGRAM",
)
WEAK = dict(
    label="WEAK",
    script=("We are a travel agency. We offer travel packages to many destinations. "
            "Contact us for more information about our services and offers."),
    caption="Travel with us. We have good offers.",
    platform="INSTAGRAM",
)
VIOLATION = dict(
    label="VIOLATION",
    script="Book our Vegas casino tour with free cocktails and nightclub access every night!",
    caption="Party hard — casino nights, open bar, and beer on us. Book now.",
    platform="INSTAGRAM",
)


def _judge(sample: dict) -> dict:
    v = judge_content(
        brand=BRAND, script=sample["script"], caption=sample["caption"],
        platform=sample["platform"],
    )
    hard = [g["name"] for g in v["guard_failures"] if g["hard"]]
    print(f"  {sample['label']:9} total={v['total']:2}/25  passed={v['passed']!s:5} "
          f"hard_guard={hard or '—'}  judge={v['judge_model']}")
    print(f"            scores={v['scores']}")
    print(f"            note  ={v['notes'][:100]!r}")
    return v


def main() -> int:
    print("== Eval-gate discrimination + FAIL-path proof (judge = Sonnet 4.6) ==")
    try:
        strong = _judge(STRONG)
        weak = _judge(WEAK)
        violation = _judge(VIOLATION)
    finally:
        with connect() as conn:
            n = conn.execute(
                "DELETE FROM \"CostLog\" WHERE \"brandId\" IS NULL AND \"toolName\" = 'eval.judge'"
            ).rowcount
        print(f"\n  (cleaned up {n} calibration CostLog rows)")

    print("\n== invariants ==")
    checks = [
        ("compliance VIOLATION is hard-blocked",
         violation["hard_failed"] and not violation["passed"]),
        ("WEAK artifact is blocked (< floor)", not weak["passed"]),
        ("judge discriminates (STRONG.total > WEAK.total by ≥6)",
         strong["total"] - weak["total"] >= 6),
    ]
    ok = True
    for label, passed in checks:
        print(f"  [{'OK ' if passed else 'FAIL'}] {label}")
        ok = ok and passed

    # Calibration signal (informational, not a fake pass): does a genuinely strong
    # piece clear the floor? If not, that's real data about judge strictness.
    print(f"\n  calibration signal — STRONG cleared the 18 floor: {strong['passed']} "
          f"(total {strong['total']}/25)")

    print("\n" + ("OK — the gate blocks weak + non-compliant content and discriminates."
                  if ok else "FAIL — gate did not discriminate as required (see above)."))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
