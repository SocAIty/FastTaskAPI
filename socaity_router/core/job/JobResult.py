from typing import Optional
from pydantic import BaseModel

from socaity_router.core.Job import InternalJob


class JobResult(BaseModel):
    """
    When the user (client) sends a request to an Endpoint, a ClientJob is created.
    This job contains the information about the request and the response.
    """
    id: str
    status: Optional[str] = None
    progress: Optional[float] = 0.0
    message: Optional[str] = None
    result: Optional[dict] = None

    created_at: Optional[str] = None
    queued_at: Optional[str] = None
    execution_started_at: Optional[str] = None
    execution_finished_at: Optional[str] = None



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
            progress=ij.job_progress.progress,
            message=ij.job_progress.message,
            result=ij.result,
            created_at=created_at,
            queued_at=queued_at,
            execution_started_at=execution_started_at,
            execution_finished_at=execution_finished_at
        )
