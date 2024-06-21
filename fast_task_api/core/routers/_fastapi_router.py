import functools
import inspect
from typing import Union

from multimodal_files.file_conversion import convert_to_upload_file_type

from fastapi import APIRouter, FastAPI
from fast_task_api.compatibility.upload import (convert_param_type_to_fast_api_upload_file,
                                                 is_param_multimodal_file)
from fast_task_api.core.job import JobProgress
from fast_task_api.CONSTS import SERVER_STATUS
from fast_task_api.core.JobManager import JobQueue
from fast_task_api.core.job.JobResult import JobResult, JobResultFactory
from fast_task_api.core.routers._socaity_router import _SocaityRouter
from fast_task_api.core.routers.router_mixins._queue_mixin import _QueueMixin


class SocaityFastAPIRouter(APIRouter, _SocaityRouter, _QueueMixin):

    def __init__(self, app: Union[FastAPI, None] = None, prefix: str = "/api", *args, **kwargs):
        """
        :param app: You can pass an existing fastapi app, if you like to have multiple routers in one app
        :param prefix: The prefix of this app for the paths
        :param args: other fastapi app arguments
        :param kwargs: other fastapi app keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.job_queue = JobQueue()
        self.status = SERVER_STATUS.INITIALIZING

        if app is None:
            app = FastAPI(
                title="FastTaskAPI",
                summary="Create web-APIs for long-running tasks",
                version="0.0.0",
                contact={
                    "name": "SocAIty",
                    "url": "https://github.com/SocAIty",
            })

        self.app = app
        self.prefix = prefix
        self.add_standard_routes()

    def add_standard_routes(self):
        self.api_route(path="/job", methods=["GET", "POST"])(self.get_job)
        self.api_route(path="/status", methods=["GET", "POST"])(self.get_status)
        # ToDo: add favicon
        #self.api_route('/favicon.ico', include_in_schema=False)(self.favicon)

    def get_job(self, job_id: str, return_format: str = 'json', keep_in_memory: bool = False) -> JobResult:
        """
        Get the job with the given job_id.
        :param job_id: The id of the job.
        :param return_format: json or gzipped
        :param keep_in_memory: If the job should be kept in memory.
            If False, the job is removed after the result is returned.
        """
        internal_job = self.job_queue.get_job(job_id, keep_in_memory=keep_in_memory)
        if internal_job is None:
            return JobResultFactory.job_not_found(job_id)

        ret_job = JobResultFactory.from_internal_job(internal_job)
        ret_job.refresh_job_url = f"/job?job_id={ret_job.id}"

        if return_format != 'json':
            ret_job = JobResultFactory.gzip_job_result(ret_job)

        return ret_job

    @staticmethod
    def _job_progress_signature_change(func: callable) -> callable:
        # either param type is JobProgress or the name is job_progress
        for param in inspect.signature(func).parameters.values():
            if param.annotation == JobProgress or param.name == "job_progress":
                # exclude the job_progress parameter from the signature
                # note that because the queue_router_decorator_func was used before,
                # the job_progress param was already registered.
                new_sig = inspect.signature(func).replace(parameters=[
                    p for p in inspect.signature(func).parameters.values()
                    if p.name != "job_progress" or p.annotation != JobProgress
                ])
                func.__signature__ = new_sig
        return func

    def _handle_file_uploads(self, func: callable) -> callable:
        """
        Modify the function signature for fastapi to handle file uploads.
        Parse/Read the starlette.MultiModalFile and give it as read socaity MultiModalFile to the function while execution.
        """

        # original func parameter names: needed multiple times
        original_func_parameters = inspect.signature(func).parameters.values()
        # create a dict to store the params that are UploadFiles
        # this is used to later map the file while reading
        upload_params = {
            param.name: param.annotation
            for param in original_func_parameters
            if is_param_multimodal_file(param)
        }

        def read_file_if_is_upload_file(param_name: str, data):
            # check if we have the file in our list
            my_data_type = upload_params.get(param_name, None)
            if my_data_type is not None:
                return convert_to_upload_file_type(data, my_data_type)

                # return starlette_uploadfile_to_socaity_upload_file(data, my_data_type)
            # if is not a file, return as is
            return data

        @functools.wraps(func)
        def file_upload_wrapper(*args, **kwargs):
            # args, kwargs to _ kwargs
            org_func_names = [param.name for param in original_func_parameters]
            nkwargs = {org_func_names[i]: arg for i, arg in enumerate(args)}
            nkwargs.update(kwargs)
            # convert to socaity MultiModalFile if it is a file
            n_kwargs = {key: read_file_if_is_upload_file(key, value) for key, value in kwargs.items()}

            return func(**n_kwargs)

        # replace signature with fastapi signature
        new_sig = inspect.signature(func).replace(parameters=[
            convert_param_type_to_fast_api_upload_file(param)
            if is_param_multimodal_file(param) else param
            for param in original_func_parameters
        ])
        file_upload_wrapper.__signature__ = new_sig
        func.__signature__ = new_sig

        return file_upload_wrapper

        ## modify execution to handle file uploads in the same way as in runpod
        #def func_with_file_upload(*args, **kwargs):
        #    for param in inspect.signature(func).parameters.values():
        #        if param.annotation == compatibility.UploadDataType:
        #            file = kwargs[param.name]
        #            if isinstance(file, str):
        #                try:
        #                    decoded_file = compatibility.base64_to_file(file, param.annotation)
        #                    kwargs[param.name] = decoded_file
        #                except Exception as e:
        #                    logging.error(f"Error decoding file {param.name} in upload. We pass it as is. Error: {e}")
        #    return func(*args, **kwargs)
#
        #return func_with_file_upload

    def task_endpoint(
            self,
            path: str,
            queue_size: int = 100,
            methods: list[str] = None,
            *args,
            **kwargs
    ):
        """
        Adds an additional wrapper to the API path to add functionality like:
        - Add api key validation
        - Create a job and add to the job queue
        - Return job
        """
        if len(path) > 0 and path[0] != "/":
            path = "/" + path

        fastapi_route_decorator_func = self.api_route(
            path=path,
            methods=["POST"] if methods is None else methods,
            *args,
            **kwargs
        )

        queue_router_decorator_func = super().job_queue_func(
            path=path,
            queue_size=queue_size,
            *args,
            **kwargs
        )
        def decorator(func):
            # add the queue to the job queue
            queue_decorated = queue_router_decorator_func(func)
            # remove job_progress from the function signature to display nice for fastapi
            job_progress_removed = self._job_progress_signature_change(queue_decorated)
            # modify file uploads for compatibility reasons
            file_upload_modified = self._handle_file_uploads(job_progress_removed)
            # modify file responses so that functions can return multimodal files.
            # file_response_modified = self._handle_file_responses(file_upload_modified)
            # add the route to fastapi
            return fastapi_route_decorator_func(file_upload_modified)

        return decorator

    def get(self, path: str = None, queue_size: int = 100, *args, **kwargs):
        return self.task_endpoint(path=path, queue_size=queue_size, methods=["GET"], *args, **kwargs)

    def post(self, path: str = None, queue_size: int = 100, *args, **kwargs):
        return self.task_endpoint(path=path, queue_size=queue_size, methods=["POST"], *args, **kwargs)

    def start(self, environment="localhost", port=8000):
        """
        Start the FastAPI server and add this app.
        """
        # fast API start
        if self.app is None:
            self.app = FastAPI()

        self.app.include_router(self)
        print(f"FastTaskAPI {self.app.title} started. Use http://localhost:{port}/docs to see the API documentation.")
        import uvicorn
        uvicorn.run(self.app, host=environment, port=port)

