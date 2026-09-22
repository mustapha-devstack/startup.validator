from __future__ import annotations

from langchain_tavily import TavilySearch

from agents.base import emit_event, get_llm
from schemas.models import (
    AgentEventType,
    AgentName,
    AgentStatus,
)

from core.config import TAVILY_API_KEY


async def run_monetisation_agent(
    job_id: str,
    idea: str,
) -> dict[str, object]:
    agent = AgentName.MONETISATION

    await emit_event(
        job_id,
        agent,
        AgentStatus.RUNNING,
        AgentEventType.STATUS,
        "Evaluating monetisation opportunities...",
        10,
    )

    search = TavilySearch(
        tavily_api_key=TAVILY_API_KEY,
        max_results=5,
        topic="general",
    )

    research = await search.ainvoke(
        {
            "query": (
                f"pricing business models monetisation "
                f"companies in market for: {idea}"
            )
        }
    )

    await emit_event(
        job_id,
        agent,
        AgentStatus.RUNNING,
        AgentEventType.PROGRESS,
        "Pricing research collected.",
        45,
    )

    llm = get_llm()

    response = await llm.ainvoke(
        [
            (
                "system",
                """
You are the Monetisation agent.

Determine how this startup could make money.

Analyze:
- customer willingness to pay
- pricing models
- revenue streams
- unit economics considerations
- acquisition economics
- monetisation risks
- possible pricing experiments

Avoid fabricated market prices.
""",
            ),
            (
                "human",
                f"""
Startup idea:

{idea}

Research:

{research}
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
        "research": research,
    }