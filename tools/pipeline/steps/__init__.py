"""The one step registry — the binding between manifest `step:` names and code.

Keep this map import-light: values are `"module:function"` strings resolved
lazily, so the drift guard (scripts/check-pipeline-drift.py) and any static
tooling can read the registry WITHOUT importing the LLM gateway / DB stack.
"""
from __future__ import annotations

import importlib
from typing import Callable

# manifest `step:` name → "module:function" (lazy import target).
STEP_REGISTRY: dict[str, str] = {
    "trends": "tools.pipeline.steps.trends:run",
    "strategy": "tools.pipeline.steps.strategy:run",
    "creative": "tools.pipeline.steps.creative:run",
    "eval_gate": "tools.pipeline.steps.eval_gate:run",
}


class UnknownStep(KeyError):
    """A manifest names a step with no registered implementation."""


def resolve(name: str) -> Callable:
    """Import and return the implementation for a registered step name."""
    try:
        target = STEP_REGISTRY[name]
    except KeyError as exc:
        raise UnknownStep(
            f"Step {name!r} is not in STEP_REGISTRY (known: {', '.join(STEP_REGISTRY)})."
        ) from exc
    module_path, func_name = target.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, func_name)
