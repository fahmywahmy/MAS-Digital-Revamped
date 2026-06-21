"""Manifest-driven pipeline runner — the one execution path for content runs.

A YAML manifest under `pipelines/` is the single source of truth (no parallel
hardcoded orchestrator). `runner.run_pipeline()` walks the manifest's steps,
each calling the LLM gateway (so real cost accrues onto the AgentRun) and
persisting its artifact, with the eval gate as a hard pre-publish floor.
"""
