from typing import Optional, Union
from pydantic import BaseModel

from socaity_router.core.job import InternalJob
from socaity_router.core.job.InternalJob import JOB_STATUS


class JobResult(BaseModel):
    """
    When the user (client) sends a request to an Endpoint, a ClientJob is created.
    This job contains the information about the request and the response.
    """
    id: str
    status: Optional[str] = None
    progress: Optional[float] = 0.0
    message: Optional[str] = None
    result: Optional[object] = None
    refresh_job_url: Optional[str] = None

    created_at: Optional[str] = None
    queued_at: Optional[str] = None
    execution_started_at: Optional[str] = None
    execution_finished_at: Optional[str] = None

    endpoint_protocol: Optional[str] = "socaity"


class JobResultFactory:
    @staticmethod
    def from_internal_job(ij: InternalJob):
        format_date = lambda date: date.strftime("%Y-%m-%dT%H:%M:%S.%f%z") if date else None
        created_at = format_date(ij.created_at)
        queued_at = format_date(ij.queued_at)
        execution_started_at = format_date(ij.execution_started_at)
        execution_finished_at = format_date(ij.execution_finished_at)

        return JobResult(
            id=ij.id,
            status=ij.status,
            progress=ij.job_progress._progress,
            message=ij.job_progress._message,
            result=ij.result,
            created_at=created_at,
            queued_at=queued_at,
            execution_started_at=execution_started_at,
            execution_finished_at=execution_finished_at
        )

    @staticmethod
    def job_not_found(job_id: str) -> JobResult:
        return JobResult(
            id=job_id,
            status=JOB_STATUS.FAILED,
            message="Job not found.",
        )