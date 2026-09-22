from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from schemas.models import (
    AgentEvent,
    JobStatus,
    ValidationJob,
    ValidationResult,
)


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, ValidationJob] = {}
        self._events: dict[str, list[AgentEvent]] = {}
        self._conditions: dict[str, asyncio.Condition] = {}

    async def create_job(self, job_id: str) -> ValidationJob:
        now = datetime.now(UTC)

        job = ValidationJob(
            job_id=job_id,
            status=JobStatus.QUEUED,
            created_at=now,
            updated_at=now,
        )

        self._jobs[job_id] = job
        self._events[job_id] = []
        self._conditions[job_id] = asyncio.Condition()

        return job

    async def get_job(self, job_id: str) -> ValidationJob | None:
        return self._jobs.get(job_id)

    async def set_status(
        self,
        job_id: str,
        status: JobStatus,
        error: str | None = None,
    ) -> None:
        job = self._jobs.get(job_id)

        if job is None:
            return

        job.status = status
        job.updated_at = datetime.now(UTC)

        if error is not None:
            job.error = error

        await self._notify(job_id)

    async def set_result(
        self,
        job_id: str,
        result: ValidationResult,
    ) -> None:
        job = self._jobs.get(job_id)

        if job is None:
            return

        job.result = result
        job.status = JobStatus.COMPLETED
        job.updated_at = datetime.now(UTC)

        await self._notify(job_id)

    async def add_event(
        self,
        event: AgentEvent,
    ) -> None:
        if event.job_id not in self._events:
            return

        self._events[event.job_id].append(event)

        await self._notify(event.job_id)

    async def get_events(
        self,
        job_id: str,
        offset: int = 0,
    ) -> list[AgentEvent]:
        events = self._events.get(job_id, [])

        return events[offset:]

    async def wait_for_events(
        self,
        job_id: str,
        timeout: float = 15.0,
    ) -> None:
        condition = self._conditions.get(job_id)

        if condition is None:
            return

        try:
            async with condition:
                await asyncio.wait_for(
                    condition.wait(),
                    timeout=timeout,
                )
        except asyncio.TimeoutError:
            pass

    async def _notify(self, job_id: str) -> None:
        condition = self._conditions.get(job_id)

        if condition is None:
            return

        async with condition:
            condition.notify_all()


job_store = JobStore()