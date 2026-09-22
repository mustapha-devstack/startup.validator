from __future__ import annotations

from langchain_tavily import TavilySearch

from agents.base import emit_event, get_llm
from schemas.models import (
    AgentEventType,
    AgentName,
    AgentStatus,
)

from core.config import TAVILY_API_KEY


async def run_risk_agent(
    job_id: str,
    idea: str,
) -> dict[str, object]:
    agent = AgentName.RISK

    await emit_event(
        job_id,
        agent,
        AgentStatus.RUNNING,
        AgentEventType.STATUS,
        "Evaluating startup risks...",
        10,
    )

    search = TavilySearch(
        tavily_api_key=TAVILY_API_KEY,
        max_results=6,
        topic="general",
    )
    research = await search.ainvoke(
        {
            "query": (
                f"regulatory risks legal risks operational risks "
                f"technology risks for: {idea}"
            )
        }
    )

    await emit_event(
        job_id,
        agent,
        AgentStatus.RUNNING,
        AgentEventType.PROGRESS,
        "Risk research collected.",
        45,
    )

    llm = get_llm()

    response = await llm.ainvoke(
        [
            (
                "system",
                """
You are the Risk Assessment agent.

Evaluate the startup idea for:
- market risks
- regulatory risks
- operational risks
- technical risks
- financial risks
- adoption risks
- execution risks

For each major risk explain severity,
likelihood and possible mitigation.

Do not invent regulations or facts.
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