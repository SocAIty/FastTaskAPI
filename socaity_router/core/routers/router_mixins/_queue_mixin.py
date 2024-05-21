import functools

from socaity_router.CONSTS import SERVER_STATUS
from socaity_router.core.JobQueue import JobQueue
from socaity_router.core.job.JobResult import JobResultFactory, JobResult

class _QueueMixin:
    """
    Adds a job queue to a router.
    Then instead of returning the result of the function, it returns a job object.
    Jobs are executed in threads. The user can check the status of the job and get the result.
    """
    def __init__(self):
        self.job_queue = JobQueue()
        self.status = SERVER_STATUS.INITIALIZING

        # add the get_status function to the routes
        # self.add_api_route(path="/status")

    def job_queue_func(
            self,
            queue_size: int = 100,
            *args,
            **kwargs
    ):
        """
        Adds an additional wrapper to the API path to add functionality like:
        - Add api key validation
        - Create a job and add to the job queue
        - Return job
        """

        # add the queue to the job queue
        def decorator(func):
            self.job_queue.set_queue_size(func, queue_size)

            @functools.wraps(func)
            def job_creation_func_wrapper(*wrapped_func_args, **wrapped_func_kwargs) -> JobResult:
                # combine args and kwargs
                wrapped_func_kwargs.update(wrapped_func_args)
                # create a job and add to the job queue
                internal_job = self.job_queue.add_job(
                    job_function=func,
                    job_params=wrapped_func_kwargs
                )
                ret_job = JobResultFactory.from_internal_job(internal_job)
                return ret_job

            return job_creation_func_wrapper

        return decorator

