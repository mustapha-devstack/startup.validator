from __future__ import annotations

from langchain_tavily import TavilySearch

from agents.base import emit_event, get_llm
from schemas.models import (
    AgentEventType,
    AgentName,
    AgentStatus,
)
from core.config import TAVILY_API_KEY


async def run_competitor_agent(
    job_id: str,
    idea: str,
) -> dict[str, object]:
    agent = AgentName.COMPETITOR

    await emit_event(
        job_id,
        agent,
        AgentStatus.RUNNING,
        AgentEventType.STATUS,
        "Identifying competitors...",
        10,
    )

    search = TavilySearch(
        tavily_api_key=TAVILY_API_KEY,
        max_results=8,
        topic="general",
    )

    results = await search.ainvoke(
        {
            "query": (
                f"competitors alternatives startups companies "
                f"products solving: {idea}"
            )
        }
    )

    await emit_event(
        job_id,
        agent,
        AgentStatus.RUNNING,
        AgentEventType.PROGRESS,
        "Competitor research collected.",
        45,
    )

    llm = get_llm()

    response = await llm.ainvoke(
        [
            (
                "system",
                """
You are the Competitive Analysis agent.

Identify direct and indirect competitors.

Analyze:
- competitor positioning
- strengths
- weaknesses
- differentiation opportunities
- barriers to entry
- potential competitive threats

Separate verified information from inference.
Do not invent company facts.
""",
            ),
            (
                "human",
                f"""
Startup idea:

{idea}

Web research:

{results}
""",
            ),
        ]
    )

    content = str(response.content)

    await emit_event(
        job_id,
        agent,
        AgentStatus.COMPLETED,
        AgentEventType.RESULT,
        content,
        100,
    )

    return {
        "agent": agent.value,
        "summary": content,
        "research": results,
    }