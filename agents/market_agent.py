from __future__ import annotations

from langchain_tavily import TavilySearch

from agents.base import emit_event, get_llm
from schemas.models import (
    AgentEventType,
    AgentName,
    AgentStatus,
)
from core.config import TAVILY_API_KEY


async def run_market_agent(
    job_id: str,
    idea: str,
) -> dict[str, object]:
    agent = AgentName.MARKET

    await emit_event(
        job_id,
        agent,
        AgentStatus.RUNNING,
        AgentEventType.STATUS,
        "Analyzing the market opportunity...",
        10,
    )

    search = TavilySearch(
        tavily_api_key=TAVILY_API_KEY,
        max_results=5,
        topic="general",
    )

    search_result = await search.ainvoke(
        {
            "query": (
                f"market size trends demand existing solutions "
                f"for startup idea: {idea}"
            )
        }
    )

    await emit_event(
        job_id,
        agent,
        AgentStatus.RUNNING,
        AgentEventType.PROGRESS,
        "Market research collected.",
        40,
    )

    llm = get_llm()

    response = await llm.ainvoke(
        [
            (
                "system",
                """
You are the Market Research agent for PlanGraph.

Evaluate a startup idea using current market information.

Analyze:
- target market
- customer demand
- market trends
- market maturity
- potential market opportunity
- important evidence
- uncertainty

Do not invent statistics.

Return a concise structured analysis.
""",
            ),
            (
                "human",
                f"""
Startup idea:

{idea}

Research gathered from the web:

{search_result}
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
        "research": search_result,
    }