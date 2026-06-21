"""Step 3 — creative. Produce the CreativeBrief + the ContentPiece (script) +
its ContentCopy (caption/hashtags). The ContentPiece starts DRAFT; the eval gate
decides whether it becomes publishable.
"""
from __future__ import annotations

import json
from typing import Any

from tools.pipeline.context import PipelineContext, brand_summary, parse_step_json
from tools.utils import claude_client
from tools.utils.db import connect
from tools.utils.ids import new_id

_SYSTEM = "You are a senior creative at a marketing agency."

_SCHEMA = {
    "type": "object",
    "properties": {
        "visual_direction": {"type": "string"},
        "beats": {"type": "array", "items": {"type": "string"}},
        "script": {"type": "string"},
        "caption": {"type": "string"},
        "hashtags": {"type": "string"},
    },
    "required": ["visual_direction", "beats", "script", "caption", "hashtags"],
    "additionalProperties": False,
}


def run(ctx: PipelineContext) -> dict[str, Any]:
    strat = ctx.out("strategy")
    content_type = ctx.step_config.get("content_type", "REEL")
    platform = ctx.step_config.get("platform", "INSTAGRAM")

    prompt = (
        f"{brand_summary(ctx.brand)}\n\n"
        f"Strategy — topic: {strat['topic']}; angle: {strat['angle']}; "
        f"hooks: {json.dumps(strat['hooks'], ensure_ascii=False)}\n"
        f"Brief: {strat['brief']}\n\n"
        f"Produce a {content_type} concept and its {platform} copy. Audience-facing "
        "text in the brand's language. `hashtags` is a single space-separated string."
    )
    res = claude_client.complete(
        prompt=prompt,
        system=_SYSTEM,
        max_tokens=2500,
        json_schema=_SCHEMA,
        agent_type=ctx.agent_type,
        category="creative",
        tool_name="pipeline.creative",
        brand_id=ctx.brand_id,
        run_id=ctx.run_id,
        budget_usd=ctx.budget_usd,
    )
    data = parse_step_json(res.text, res.stop_reason)

    creative_brief_id = new_id("cb")
    content_piece_id = new_id("cp")
    content_copy_id = new_id("cc")

    with connect(autocommit=False) as conn:
        with conn.transaction():
            conn.execute(
                '''INSERT INTO "CreativeBrief"
                       (id, "strategyBriefId", "visualDirection", "beatOutline",
                        status, "updatedAt")
                   VALUES (%s, %s, %s, %s::jsonb, %s::"CreativeStatus", now())''',
                (creative_brief_id, strat["strategy_brief_id"], data["visual_direction"],
                 json.dumps(data["beats"]), "COMPLETED"),
            )
            conn.execute(
                '''INSERT INTO "ContentPiece"
                       (id, "brandId", "creativeBriefId", type, script, status, "updatedAt")
                   VALUES (%s, %s, %s, %s::"ContentType", %s, %s::"ContentStatus", now())''',
                (content_piece_id, ctx.brand_id, creative_brief_id, content_type,
                 data["script"], "DRAFT"),
            )
            conn.execute(
                '''INSERT INTO "ContentCopy"
                       (id, "contentPieceId", platform, caption, hashtags, "updatedAt")
                   VALUES (%s, %s, %s::"Platform", %s, %s, now())''',
                (content_copy_id, content_piece_id, platform, data["caption"],
                 data.get("hashtags")),
            )

    return {
        "creative_brief_id": creative_brief_id,
        "content_piece_id": content_piece_id,
        "platform": platform,
        "script": data["script"],
        "caption": data["caption"],
        "hashtags": data.get("hashtags"),
        "cost_usd": res.cost_usd,
    }
