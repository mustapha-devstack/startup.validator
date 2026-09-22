from __future__ import annotations

import json

from agents.base import emit_event, get_llm
from schemas.models import (
    AgentEventType,
    AgentName,
    AgentStatus,
)


async def run_synthesis_agent(
    job_id: str,
    idea: str,
    research: dict[str, object],
) -> dict[str, object]:
    await emit_event(
        job_id,
        AgentName.SYNTHESIS,
        AgentStatus.RUNNING,
        AgentEventType.STATUS,
        "Synthesizing the research...",
        10.0,
    )

    llm = get_llm(max_tokens=2_048)

    research_json = json.dumps(
        research,
        ensure_ascii=False,
    )

    prompt = f"""
You are the final startup validation analyst.

Startup idea:
{idea}

Research summaries:
{research_json}

Produce a concise final validation report.

Return ONLY valid JSON in this exact structure:

{{
  "overall_score": 0,
  "verdict": "string",
  "summary": "markdown string",
  "key_recommendations": [
    "string"
  ]
}}

Rules:
- overall_score must be between 0 and 100.
- verdict must be concise.
- summary must be under 1200 words.
- key_recommendations must contain at most 5 items.
- Do not repeat the entire research.
- Focus on the most important evidence.
- Use Markdown inside the summary.
- Do not use escaped Markdown such as \\*\\* or \\##.
- Do not include HTML or SVG.
"""

    response = await llm.ainvoke(prompt)

    content = response.content

    if not isinstance(content, str):
        content = str(content)

    content = content.strip()

    # Remove accidental Markdown code fences around JSON.
    if content.startswith("```json"):
        content = content[7:]

    if content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    parsed = json.loads(content)

    await emit_event(
        job_id,
        AgentName.SYNTHESIS,
        AgentStatus.COMPLETED,
        AgentEventType.COMPLETE,
        parsed,
        100.0,
    )

    return parsed