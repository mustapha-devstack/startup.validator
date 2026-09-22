from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from core.job_store import job_store
from schemas.models import JobStatus


async def event_stream(
    job_id: str,
) -> AsyncGenerator[dict[str, str], None]:
    cursor = 0

    while True:
        job = await job_store.get_job(job_id)

        if job is None:
            yield {
                "event": "error",
                "data": json.dumps(
                    {
                        "error": "Job not found",
                    }
                ),
            }
            return

        events = await job_store.get_events(
            job_id,
            cursor,
        )

        for event in events:
            cursor += 1

            yield {
                "id": str(cursor),
                "event": "agent",
                "data": event.model_dump_json(),
            }

        job = await job_store.get_job(job_id)

        if job is None:
            return

        if job.status == JobStatus.COMPLETED:
            yield {
                "event": "done",
                "data": json.dumps(
                    {
                        "status": "completed",
                    }
                ),
            }
            return

        if job.status == JobStatus.FAILED:
            yield {
                "event": "done",
                "data": json.dumps(
                    {
                        "status": "failed",
                        "error": job.error,
                    }
                ),
            }
            return

        await job_store.wait_for_events(
            job_id,
            timeout=10.0,
        )

        # Explicit SSE heartbeat.
        yield {
            "event": "heartbeat",
            "data": json.dumps(
                {
                    "timestamp": asyncio.get_running_loop().time(),
                }
            ),
        }