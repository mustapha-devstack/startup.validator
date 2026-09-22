from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentName(str, Enum):
    MARKET = "market"
    COMPETITOR = "competitor"
    RISK = "risk"
    MONETISATION = "monetisation"
    SYNTHESIS = "synthesis"


class AgentStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentEventType(str, Enum):
    STATUS = "status"
    TOKEN = "token"
    PROGRESS = "progress"
    RESULT = "result"
    ERROR = "error"
    COMPLETE = "complete"


class ValidationRequest(BaseModel):
    idea: str = Field(
        ...,
        min_length=10,
        max_length=10_000,
        description="Startup idea to validate.",
    )

    board_id: str | None = Field(
        default=None,
        max_length=255,
    )


class AgentEvent(BaseModel):
    job_id: str
    agent: AgentName
    status: AgentStatus
    type: AgentEventType
    data: Any = None
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    timestamp: datetime


class AgentSummary(BaseModel):
    agent: AgentName
    summary: str
    findings: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ValidationResult(BaseModel):
    job_id: str

    overall_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    verdict: str

    summaries: list[AgentSummary]

    synthesis: str

    completed_at: datetime


class ValidationJob(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    result: ValidationResult | None = None
    error: str | None = None


class ValidationAccepted(BaseModel):
    job_id: str
    status: JobStatus