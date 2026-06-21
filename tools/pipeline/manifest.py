"""Load and validate a pipeline manifest (the single source of truth).

A manifest is invalid if any step names an implementation absent from the step
registry — the same check the CI drift guard runs statically.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tools.pipeline.steps import STEP_REGISTRY
from tools.utils.config import REPO_ROOT

PIPELINES_DIR = REPO_ROOT / "pipelines"


@dataclass(frozen=True)
class Step:
    name: str          # unique label within the manifest
    step: str          # registry key → implementation
    agent_type: str    # AgentType the gateway records for this step
    config: dict[str, Any]


@dataclass(frozen=True)
class Manifest:
    id: str
    name: str
    description: str
    steps: tuple[Step, ...]


class ManifestError(ValueError):
    """A manifest is malformed or names an unregistered step."""


def _parse(data: dict[str, Any], source: str) -> Manifest:
    if not data.get("id"):
        raise ManifestError(f"{source}: manifest missing `id`.")
    raw_steps = data.get("steps") or []
    if not raw_steps:
        raise ManifestError(f"{source}: manifest names no steps.")

    steps: list[Step] = []
    seen: set[str] = set()
    for i, s in enumerate(raw_steps):
        name = s.get("name") or s.get("step")
        impl = s.get("step")
        if not impl:
            raise ManifestError(f"{source}: step #{i} missing `step`.")
        if impl not in STEP_REGISTRY:
            raise ManifestError(
                f"{source}: step {name!r} → unknown implementation {impl!r} "
                f"(known: {', '.join(STEP_REGISTRY)})."
            )
        if name in seen:
            raise ManifestError(f"{source}: duplicate step name {name!r}.")
        seen.add(name)
        steps.append(
            Step(name=name, step=impl, agent_type=s.get("agent_type", "ORCHESTRATOR"),
                 config=s.get("config") or {})
        )

    return Manifest(
        id=data["id"],
        name=data.get("name", data["id"]),
        description=data.get("description", ""),
        steps=tuple(steps),
    )


def load(path: str | Path) -> Manifest:
    p = Path(path)
    return _parse(yaml.safe_load(p.read_text(encoding="utf-8")), str(p))


def load_by_id(manifest_id: str) -> Manifest:
    """Load `pipelines/<id>.yaml`."""
    return load(PIPELINES_DIR / f"{manifest_id}.yaml")


def all_manifests() -> list[Manifest]:
    """Every manifest under pipelines/ (used by the drift guard)."""
    return [load(p) for p in sorted(PIPELINES_DIR.glob("*.yaml"))]
