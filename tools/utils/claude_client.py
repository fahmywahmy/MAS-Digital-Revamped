"""The LLM gateway — the ONLY door to Anthropic (CLAUDE.md §4; CI-enforced).

No other file in the repo may `import anthropic`. Every Claude call goes through
`complete()`, which:

  1. Reads the API key once, from the one credential door.
  2. Runs the pre-call kill-switch when given a run + budget (real abort, not a
     `print()`).
  3. Makes the call, then writes real cost to the ledger (CostLog + AgentRun)
     before returning.

Defaults to Claude Opus 4.8 with adaptive thinking off for predictable, cheap
tool calls; callers opt into thinking / effort per task.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import anthropic

from tools.utils import cost_logger
from tools.utils.config import get_credential
from tools.utils.registry import DEFAULT_MODEL, price_for

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=get_credential("ANTHROPIC_API_KEY"))
    return _client


@dataclass(frozen=True)
class CompletionResult:
    text: str
    model: str
    stop_reason: str | None
    usage: dict[str, int]
    cost_usd: float
    cost_log_id: str
    run_total_usd: float | None


def _usage_dict(usage: Any) -> dict[str, int]:
    """Normalise the SDK usage object into the four ledger buckets."""
    return {
        "tokens_in": getattr(usage, "input_tokens", 0) or 0,
        "tokens_out": getattr(usage, "output_tokens", 0) or 0,
        "cache_read_tokens": getattr(usage, "cache_read_input_tokens", 0) or 0,
        "cache_creation_tokens": getattr(usage, "cache_creation_input_tokens", 0) or 0,
    }


def complete(
    *,
    prompt: str | None = None,
    messages: list[dict[str, Any]] | None = None,
    system: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
    thinking: bool = False,
    effort: str | None = None,
    # accounting (what the ledger records)
    agent_type: str = "ORCHESTRATOR",
    category: str = "general",
    tool_name: str | None = None,
    brand_id: str | None = None,
    run_id: str | None = None,
    budget_usd: float | None = None,
) -> CompletionResult:
    """Make one Claude call, log its real cost, and return the result.

    Provide exactly one of `prompt` or `messages`. When `run_id` and
    `budget_usd` are both set, the kill-switch aborts the call if the run has
    already reached its budget.
    """
    if (prompt is None) == (messages is None):
        raise ValueError("Pass exactly one of `prompt` or `messages`.")
    # Validate pricing up front so an unknown model fails before spending.
    price_for(model)

    # ── Pre-call kill-switch (real abort, not a print) ──────────────────────
    if run_id is not None and budget_usd is not None:
        cost_logger.check_budget(run_id, budget_usd)

    request: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages if messages is not None else [{"role": "user", "content": prompt}],
    }
    if system is not None:
        request["system"] = system
    if thinking:
        request["thinking"] = {"type": "adaptive"}
    if effort is not None:
        request["output_config"] = {"effort": effort}

    response = _get_client().messages.create(**request)

    text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    usage = _usage_dict(response.usage)

    logged = cost_logger.record_call(
        model=model,
        agent_type=agent_type,
        category=category,
        tool_name=tool_name,
        brand_id=brand_id,
        run_id=run_id,
        **usage,
    )

    return CompletionResult(
        text=text,
        model=response.model,
        stop_reason=response.stop_reason,
        usage=usage,
        cost_usd=logged.cost_usd,
        cost_log_id=logged.cost_log_id,
        run_total_usd=logged.run_total_usd,
    )
