from __future__ import annotations

import asyncio
import uuid

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from core.job_store import job_store
from core.orchestrator import run_validation
from core.streaming import event_stream

from schemas.models import (
    JobStatus,
    ValidationAccepted,
    ValidationRequest,
    ValidationResult,
)

router = APIRouter(
    prefix="/api",
)


@router.post(
    "/validate",
    response_model=ValidationAccepted,
)
async def validate(
    request: ValidationRequest,
) -> ValidationAccepted:
    job_id = str(uuid.uuid4())

    await job_store.create_job(job_id)

    asyncio.create_task(
        run_validation(
            job_id=job_id,
            idea=request.idea,
            board_id=request.board_id,
        )
    )

    return ValidationAccepted(
        job_id=job_id,
        status=JobStatus.QUEUED,
    )


@router.get(
    "/stream/{job_id}",
)
async def stream_validation(
    job_id: str,
) -> EventSourceResponse:
    job = await job_store.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Validation job not found",
        )

    return EventSourceResponse(
        event_stream(job_id),
        ping=15,
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@router.get(
    "/result/{job_id}",
    response_model=ValidationResult,
)
async def get_result(
    job_id: str,
) -> ValidationResult:
    job = await job_store.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Validation job not found",
        )

    if job.status == JobStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=job.error or "Validation failed",
        )

    if job.result is None:
        raise HTTPException(
            status_code=202,
            detail="Validation is still running",
        )

    return job.result