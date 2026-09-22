from __future__ import annotations

from datetime import UTC, datetime

from langchain_groq import ChatGroq

from core.config import GROQ_API_KEY, LLM_MODEL
from core.job_store import job_store
from schemas.models import (
    AgentEvent,
    AgentEventType,
    AgentName,
    AgentStatus,
)


def get_llm() -> ChatGroq:
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0.2,
        max_tokens=4_096,
    )

def get_llm(
    max_tokens: int = 2_048,
) -> ChatGroq:
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0.2,
        max_tokens=max_tokens,
    )


async def emit_event(
    job_id: str,
    agent: AgentName,
    status: AgentStatus,
    event_type: AgentEventType,
    data: object = None,
    progress: float = 0.0,
) -> None:
    event = AgentEvent(
        job_id=job_id,
        agent=agent,
        status=status,
        type=event_type,
        data=data,
        progress=progress,
        timestamp=datetime.now(UTC),
    )

    await job_store.add_event(event)