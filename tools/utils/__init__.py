"""Shared infrastructure for the toolchain: the LLM gateway, cost ledger,
credential door, model registry, and DB connection helper.

One source of truth per concern (CLAUDE.md §2.2):
  - `claude_client`  — the only door to Anthropic
  - `cost_logger`    — the only writer of CostLog + AgentRun spend
  - `config`         — the only credential door (`get_credential`)
  - `registry`       — the only model/pricing table
  - `db`             — the only Postgres connection helper for the tools
"""
