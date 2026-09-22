from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from agents.competitor_agent import run_competitor_agent
from agents.market_agent import run_market_agent
from agents.monetisation_agent import run_monetisation_agent
from agents.risk_agent import run_risk_agent
from agents.synthesis_agent import run_synthesis_agent

from core.job_store import job_store
from schemas.models import (
    AgentName,
    AgentSummary,
    JobStatus,
    ValidationResult,
)

from typing import Annotated, TypedDict


def merge_research(
    current: dict[str, object],
    update: dict[str, object],
) -> dict[str, object]:
    return {
        **current,
        **update,
    }


class ValidationState(TypedDict):
    job_id: str
    idea: str
    board_id: str | None

    research: Annotated[
        dict[str, object],
        merge_research,
    ]

    synthesis: dict[str, object]


async def supervisor(
    state: ValidationState,
) -> dict[str, object]:
    return {}


def fan_out(
    state: ValidationState,
) -> list[Send]:
    job_id = state["job_id"]
    idea = state["idea"]

    return [
        Send(
            "market",
            {
                "job_id": job_id,
                "idea": idea,
            },
        ),
        Send(
            "competitor",
            {
                "job_id": job_id,
                "idea": idea,
            },
        ),
        Send(
            "risk",
            {
                "job_id": job_id,
                "idea": idea,
            },
        ),
        Send(
            "monetisation",
            {
                "job_id": job_id,
                "idea": idea,
            },
        ),
    ]


async def market(
    state: dict[str, object],
) -> dict[str, object]:
    result = await run_market_agent(
        str(state["job_id"]),
        str(state["idea"]),
    )

    return {
        "research": {
            AgentName.MARKET.value: result,
        }
    }


async def competitor(
    state: dict[str, object],
) -> dict[str, object]:
    result = await run_competitor_agent(
        str(state["job_id"]),
        str(state["idea"]),
    )

    return {
        "research": {
            AgentName.COMPETITOR.value: result,
        }
    }


async def risk(
    state: dict[str, object],
) -> dict[str, object]:
    result = await run_risk_agent(
        str(state["job_id"]),
        str(state["idea"]),
    )

    return {
        "research": {
            AgentName.RISK.value: result,
        }
    }


async def monetisation(
    state: dict[str, object],
) -> dict[str, object]:
    result = await run_monetisation_agent(
        str(state["job_id"]),
        str(state["idea"]),
    )

    return {
        "research": {
            AgentName.MONETISATION.value: result,
        }
    }


async def synthesis(state: ValidationState) -> dict[str, object]:
    compact_research: dict[str, object] = {}

    # Keep the synthesis input deliberately small.
    # 1,500 characters per agent is roughly 350–450 tokens.
    max_summary_chars = 1_500

    for agent_name, result in state["research"].items():
        if not isinstance(result, dict):
            continue

        summary = result.get("summary", "")

        if not isinstance(summary, str):
            summary = str(summary)

        # Keep only the most useful portion of each research summary.
        compact_research[agent_name] = {
            "summary": summary[:max_summary_chars],
        }

    result = await run_synthesis_agent(
        job_id=state["job_id"],
        idea=state["idea"],
        research=compact_research,
    )

    return {
        "synthesis": result,
    }

def build_graph():
    graph = StateGraph(ValidationState)

    graph.add_node("supervisor", supervisor)

    graph.add_node("market", market)
    graph.add_node("competitor", competitor)
    graph.add_node("risk", risk)
    graph.add_node("monetisation", monetisation)

    graph.add_node("synthesis", synthesis)

    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        fan_out,
    )

    graph.add_edge("market", "synthesis")
    graph.add_edge("competitor", "synthesis")
    graph.add_edge("risk", "synthesis")
    graph.add_edge("monetisation", "synthesis")

    graph.add_edge("synthesis", END)

    return graph.compile()

async def run_validation(
    job_id: str,
    idea: str,
    board_id: str | None,
) -> None:
    try:
        print(
            f"[validator] Starting job {job_id}"
        )

        await job_store.set_status(
            job_id,
            JobStatus.RUNNING,
        )

        initial_state: ValidationState = {
            "job_id": job_id,
            "idea": idea,
            "board_id": board_id,
            "research": {},
            "synthesis": {},
        }

        print(
            f"[validator] Invoking LangGraph for {job_id}"
        )

        final_state = await validation_graph.ainvoke(
            initial_state,
        )

        print(
            f"[validator] LangGraph completed for {job_id}"
        )

        synthesis_data = final_state.get(
            "synthesis",
            {},
        )

        raw_content = str(
            synthesis_data.get(
                "summary",
                "",
            )
        )

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            parsed = {
                "overall_score": 0,
                "verdict": "Unable to determine",
                "synthesis": raw_content,
            }

        summaries: list[AgentSummary] = []

        research = final_state.get(
            "research",
            {},
        )

        for agent_name, data in research.items():
            if not isinstance(data, dict):
                continue

            summary = str(
                data.get(
                    "summary",
                    "",
                )
            )

            summaries.append(
                AgentSummary(
                    agent=AgentName(agent_name),
                    summary=summary,
                )
            )

        result = ValidationResult(
            job_id=job_id,
            overall_score=float(
                parsed.get(
                    "overall_score",
                    0,
                )
            ),
            verdict=str(
                parsed.get(
                    "verdict",
                    "Unable to determine",
                )
            ),
            summaries=summaries,
            synthesis=str(
                parsed.get(
                    "synthesis",
                    raw_content,
                )
            ),
            completed_at=datetime.now(UTC),
        )

        await job_store.set_result(
            job_id,
            result,
        )

        print(
            f"[validator] Job {job_id} completed successfully"
        )

    except Exception as exc:
        print(
            f"[validator] Job {job_id} failed:"
        )

        import traceback

        traceback.print_exc()

        error_message = (
            f"{type(exc).__name__}: {exc}"
        )

        await job_store.set_status(
            job_id,
            JobStatus.FAILED,
            error=error_message,
        )

validation_graph = build_graph()