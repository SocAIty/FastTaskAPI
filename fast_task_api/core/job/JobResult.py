import gzip
from io import BytesIO
from typing import Optional, Union, Any

from pydantic import BaseModel
from fast_task_api.compatibility.upload import is_param_multimodal_file
from fast_task_api.core.job import InternalJob
from fast_task_api.core.job.InternalJob import JOB_STATUS


class FileResult(BaseModel):
    file_name: str
    content_type: str
    content: str  # base64 encoded


class JobResult(BaseModel):
    """
    When the user (client) sends a request to an Endpoint, a ClientJob is created.
    This job contains the information about the request and the response.
    """
    id: str
    status: Optional[str] = None
    progress: Optional[float] = 0.0
    message: Optional[str] = None
    result: Union[FileResult, Any, None] = None
    refresh_job_url: Optional[str] = None

    created_at: Optional[str] = None
    queued_at: Optional[str] = None
    execution_started_at: Optional[str] = None
    execution_finished_at: Optional[str] = None

    endpoint_protocol: Optional[str] = "socaity"


class JobResultFactory:

    @staticmethod
    def from_internal_job(ij: InternalJob) -> JobResult:
        format_date = lambda date: date.strftime("%Y-%m-%dT%H:%M:%S.%f%z") if date else None
        created_at = format_date(ij.created_at)
        queued_at = format_date(ij.queued_at)
        execution_started_at = format_date(ij.execution_started_at)
        execution_finished_at = format_date(ij.execution_finished_at)

        # if the internal job returned a multimodal file, convert it to a json serializable FileResult
        result = ij.result
        if is_param_multimodal_file(ij.result):
            result = FileResult(**result.to_json())

        return JobResult(
            id=ij.id,
            status=ij.status,
            progress=ij.job_progress._progress,
            message=ij.job_progress._message,
            result=result,
            created_at=created_at,
            queued_at=queued_at,
            execution_started_at=execution_started_at,
            execution_finished_at=execution_finished_at
        )

    @staticmethod
    def gzip_job_result(job_result: JobResult) -> bytes:
        job_result_bytes = job_result.json().encode('utf-8')
        # Compress the serialized bytes with gzip
        gzip_buffer = BytesIO()
        with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as gzip_file:
            gzip_file.write(job_result_bytes)

        # Retrieve the gzipped data
        return gzip_buffer.getvalue()


    @staticmethod
    def job_not_found(job_id: str) -> JobResult:
        return JobResult(
            id=job_id,
            status=JOB_STATUS.FAILED,
            message="Job not found.",
        )