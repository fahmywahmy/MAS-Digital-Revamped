"""Step 1 — trends. Surface content opportunities for the brand from a seed,
persist a TrendScan, and hand the top opportunity downstream.
"""
from __future__ import annotations

import json
from typing import Any

from tools.pipeline.context import PipelineContext, brand_summary, parse_step_json
from tools.utils import claude_client
from tools.utils.db import connect
from tools.utils.ids import new_id

_SYSTEM = "You are a social-media trend strategist at a marketing agency."

_SCHEMA = {
    "type": "object",
    "properties": {
        "opportunities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "rationale": {"type": "string"},
                    "hook": {"type": "string"},
                },
                "required": ["title", "rationale", "hook"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["opportunities"],
    "additionalProperties": False,
}


def run(ctx: PipelineContext) -> dict[str, Any]:
    prompt = (
        f"{brand_summary(ctx.brand)}\n\n"
        f"Seed / theme: {ctx.seed}\n\n"
        "Propose exactly 3 timely content opportunities for this brand. "
        "Write any audience-facing text in the brand's language."
    )
    res = claude_client.complete(
        prompt=prompt,
        system=_SYSTEM,
        max_tokens=1200,
        json_schema=_SCHEMA,
        agent_type=ctx.agent_type,
        category="trends",
        tool_name="pipeline.trends",
        brand_id=ctx.brand_id,
        run_id=ctx.run_id,
        budget_usd=ctx.budget_usd,
    )
    data = parse_step_json(res.text, res.stop_reason)
    opportunities = data["opportunities"]

    trend_scan_id = new_id("ts")
    with connect() as conn:
        conn.execute(
            '''INSERT INTO "TrendScan" (id, "brandId", opportunities, status, "updatedAt")
               VALUES (%s, %s, %s::jsonb, %s::"TrendStatus", now())''',
            (trend_scan_id, ctx.brand_id, json.dumps(opportunities), "COMPLETED"),
        )

    return {
        "trend_scan_id": trend_scan_id,
        "opportunities": opportunities,
        "chosen": opportunities[0],
        "cost_usd": res.cost_usd,
    }
