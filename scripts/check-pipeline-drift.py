"""Pipeline drift guard (CI-enforced; CLAUDE.md §C3).

Asserts the single-source-of-truth invariant for pipelines:

  1. Every manifest under pipelines/ loads, and every `step:` it names resolves
     to a registered implementation (manifest.load raises otherwise).
  2. The runner stays manifest-driven — it must NOT hardcode step names (the
     legacy rot was a parallel hardcoded orchestrator list). We assert no step
     key appears as a literal in runner.py.

Intentionally import-light: needs only pyyaml + the registry, no DB / no
anthropic — so it runs in CI without secrets.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.pipeline import manifest  # noqa: E402
from tools.pipeline.steps import STEP_REGISTRY  # noqa: E402


def main() -> int:
    errors: list[str] = []

    try:
        manifests = manifest.all_manifests()
    except manifest.ManifestError as exc:
        print(f"FAIL: {exc}")
        return 1

    if not manifests:
        print("FAIL: no manifests found under pipelines/")
        return 1

    for mf in manifests:
        for step in mf.steps:
            if step.step not in STEP_REGISTRY:
                errors.append(f"{mf.id}: step {step.name!r} → unregistered {step.step!r}")
        print(f"OK: {mf.id} ({len(mf.steps)} steps) all resolve")

    runner_src = (REPO_ROOT / "tools" / "pipeline" / "runner.py").read_text(encoding="utf-8")
    for key in STEP_REGISTRY:
        if f'"{key}"' in runner_src or f"'{key}'" in runner_src:
            errors.append(
                f"runner.py hardcodes step literal {key!r} — the runner must walk "
                f"the manifest, not name steps directly."
            )

    if errors:
        print("\nFAIL: pipeline drift detected:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\nOK: pipelines are manifest-driven and every step resolves.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
