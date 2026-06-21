# Integrations — MAS Digital Revamped

> External integrations are added one at a time as the tool that needs each one is
> ported, and documented here *when wired and working* (never the legacy's "25
> speculative integrations" sprawl). Each entry names: the service, the env var(s) it
> reads, and the single code path that touches it.
>
> See [`../PORTING_PLAN.md`](../PORTING_PLAN.md).

## Anthropic (Claude) — ✅ wired

| | |
|---|---|
| **Service** | Anthropic Messages API (Claude). Default model `claude-opus-4-8`; `claude-sonnet-4-6` / `claude-haiku-4-5` also priced. |
| **Env var** | `ANTHROPIC_API_KEY` — read once, via the one credential door `get_credential()`. |
| **Single code path** | `tools/utils/claude_client.py` — the **only** file that imports `anthropic` (CI-enforced). Callers use `complete()`; pricing lives in `tools/utils/registry.py`; spend is written by `tools/utils/cost_logger.py`. |
| **Proof** | `python scripts/prove-gateway.py` (see [`SETUP.md`](SETUP.md) §5). |
