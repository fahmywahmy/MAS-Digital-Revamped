"""Step 2 — strategy. Turn the chosen trend opportunity into a StrategyBrief
(topic / angle / hooks / buyer stage / brief).
"""
from __future__ import annotations

import json
from typing import Any

from tools.pipeline.context import PipelineContext, brand_summary, parse_step_json
from tools.utils import claude_client
from tools.utils.db import connect
from tools.utils.ids import new_id

_SYSTEM = "You are a content strategist at a marketing agency."
_BUYER_STAGES = ["AWARENESS", "CONSIDERATION", "DECISION", "IMPLEMENTATION"]

_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "angle": {"type": "string"},
        "hooks": {"type": "array", "items": {"type": "string"}},
        "buyer_stage": {"type": "string", "enum": _BUYER_STAGES},
        "brief": {"type": "string"},
    },
    "required": ["topic", "angle", "hooks", "buyer_stage", "brief"],
    "additionalProperties": False,
}


def run(ctx: PipelineContext) -> dict[str, Any]:
    chosen = ctx.out("trends")["chosen"]
    prompt = (
        f"{brand_summary(ctx.brand)}\n\n"
        f"Chosen opportunity: {json.dumps(chosen, ensure_ascii=False)}\n\n"
        "Write a content strategy brief for it (give 3 hooks). Audience-facing text "
        "in the brand's language."
    )
    res = claude_client.complete(
        prompt=prompt,
        system=_SYSTEM,
        max_tokens=2000,
        json_schema=_SCHEMA,
        agent_type=ctx.agent_type,
        category="strategy",
        tool_name="pipeline.strategy",
        brand_id=ctx.brand_id,
        run_id=ctx.run_id,
        budget_usd=ctx.budget_usd,
    )
    data = parse_step_json(res.text, res.stop_reason)
    stage = str(data.get("buyer_stage", "")).upper()
    buyer_stage = stage if stage in _BUYER_STAGES else None

    strategy_brief_id = new_id("sb")
    with connect() as conn:
        conn.execute(
            '''INSERT INTO "StrategyBrief"
                   (id, "brandId", "trendScanId", topic, angle, hooks, "briefContent",
                    "buyerStage", status, "updatedAt")
               VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s::"BuyerStage",
                       %s::"StrategyStatus", now())''',
            (
                strategy_brief_id, ctx.brand_id, ctx.out("trends")["trend_scan_id"],
                data["topic"], data["angle"], json.dumps(data["hooks"]),
                data["brief"], buyer_stage, "COMPLETED",
            ),
        )

    return {
        "strategy_brief_id": strategy_brief_id,
        "topic": data["topic"],
        "angle": data["angle"],
        "hooks": data["hooks"],
        "brief": data["brief"],
        "buyer_stage": buyer_stage,
        "cost_usd": res.cost_usd,
    }
