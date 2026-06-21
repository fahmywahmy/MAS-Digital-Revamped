"""The one model + pricing table (CLAUDE.md §2.2).

Prices are USD per 1,000,000 tokens, from the Anthropic pricing reference
(cached 2026-06). Cache pricing is derived from the input rate per Anthropic's
published multipliers:
  - cache READ          ≈ 0.10× input  (a cached prefix served back)
  - cache WRITE (5-min) ≈ 1.25× input  (default ephemeral TTL)

`CostLog` distinguishes `tokensIn` (uncached input, full rate),
`cacheReadTokens`, and `cacheCreationTokens` — so we price all four buckets
separately and never under-count a cache-heavy call.
"""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MODEL = "claude-opus-4-8"

# Per Anthropic's published cache economics (shared/prompt-caching.md).
_CACHE_READ_MULT = 0.10
_CACHE_WRITE_5M_MULT = 1.25


@dataclass(frozen=True)
class ModelPrice:
    input: float   # USD / 1M input tokens (uncached)
    output: float  # USD / 1M output tokens
    context: int   # context window (tokens) — informational

    @property
    def cache_read(self) -> float:
        return self.input * _CACHE_READ_MULT

    @property
    def cache_write(self) -> float:
        return self.input * _CACHE_WRITE_5M_MULT


# Current models (Anthropic pricing, cached 2026-06). Exact IDs only.
PRICES: dict[str, ModelPrice] = {
    "claude-opus-4-8":   ModelPrice(input=5.0, output=25.0, context=1_000_000),
    "claude-sonnet-4-6": ModelPrice(input=3.0, output=15.0, context=1_000_000),
    "claude-haiku-4-5":  ModelPrice(input=1.0, output=5.0,  context=200_000),
}


class UnknownModel(KeyError):
    """Pricing requested for a model not in the registry."""


def price_for(model: str) -> ModelPrice:
    try:
        return PRICES[model]
    except KeyError as exc:
        raise UnknownModel(
            f"No pricing for model {model!r}. Add it to tools/utils/registry.py "
            f"before using it through the gateway (known: {', '.join(PRICES)})."
        ) from exc


def cost_usd(
    model: str,
    *,
    tokens_in: int,
    tokens_out: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
) -> float:
    """Compute the USD cost of one call from its token usage buckets."""
    p = price_for(model)
    total = (
        tokens_in * p.input
        + tokens_out * p.output
        + cache_read_tokens * p.cache_read
        + cache_creation_tokens * p.cache_write
    )
    return total / 1_000_000
