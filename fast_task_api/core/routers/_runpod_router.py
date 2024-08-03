import functools
import importlib
import inspect
from typing import Union

from fast_task_api.CONSTS import SERVER_STATUS
from fast_task_api.core.job.JobProgress import JobProgressRunpod, JobProgress
from fast_task_api.core.routers._socaity_router import _SocaityRouter

from fast_task_api.CONSTS import FTAPI_DEPLOYMENTS
from fast_task_api.settings import FTAPI_DEPLOYMENT


class SocaityRunpodRouter(_SocaityRouter):
    """
    Adds routing functionality for the runpod serverless framework.
    The runpod_handler has an additional argument "path" which is the path to the function.
    Implementation is inspired by the fastapi app.
    The app is a runpod handler that routes the path to the correct function.
    All the runpod functionality is supported, jobs return an ID. Result can be fetched with the ID.
    """

    def __init__(self, title: str = "FastTaskAPI for ", summary: str = None, *args, **kwargs):
        super().__init__(title=title, summary=summary, *args, **kwargs)
        self.routes = {}  # routes are organized like {"ROUTE_NAME": "ROUTE_FUNCTION"}

    def task_endpoint(
            self,
            path: str = None,
            *args,
            **kwargs
    ):
        """
        Adds an additional wrapper to the API path to add functionality like:
        - Add api key validation
        - Create a job and add to the job queue
        - Return job
        """
        if len(path) > 0 and path[0] == "/":
            path = path[1:]

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*wrapped_func_args, **wrapped_func_kwargs):
                self.status = SERVER_STATUS.BUSY
                ret = func(*wrapped_func_args, **wrapped_func_kwargs)
                self.server_status = SERVER_STATUS.RUNNING
                return ret

            self.routes[path] = wrapper
            return wrapper

        return decorator

    def get(self, path: str = None, queue_size: int = 1, *args, **kwargs):
        return self.task_endpoint(path=path, queue_size=queue_size, *args, **kwargs)

    def post(self, path: str = None, queue_size: int = 1, *args, **kwargs):
        return self.task_endpoint(path=path, queue_size=queue_size, *args, **kwargs)

    def _add_job_progress_to_kwargs(self, func, job, kwargs):
        """
        If the function has a job_progress parameter, it is passed to the function normally.
        The parameter changes the progress of the runpod job.
        :param func: the function that is called
        :param job: the runpod job
        :param kwargs: the arguments that are passed to the function
        :return: the arguments with the job_progress object added if necessary
        """
        # Therefore instead of initiating a normal JobProgress object a specialized RunpodProgress object is initiated.
        # The RunpodProgress object has a reference to the runpopd job.

        job_progress_params = []
        for param in inspect.signature(func).parameters.values():
            if param.annotation == JobProgress or param.name == "job_progress":
                job_progress_params.append(param.name)

        if len(job_progress_params) > 0:
            jp = JobProgressRunpod(job)
            for job_progress_param in job_progress_params:
                kwargs[job_progress_param] = jp

        return kwargs

    @staticmethod
    def _handle_file_uploads(func: callable, **kwargs):
        """
        Params of the function that are annotated with UploadDataType will be replaced with the file content.
        """
        return kwargs

    def _router(self, path, job, **kwargs):
        """
        Internal app function that routes the path to the correct function.
        :param path: the path (route) to the function
        :param job: the runpod job (used for progress updates)
        :param kwargs: arguments for the function behind the path
        :return:
        """

        if len(path) > 0 and path[0] == "/":
            path = path[1:]

        route_function = self.routes.get(path, None)
        if route_function is None:
            raise Exception(f"Route {path} not found")

        # add the runpod job_progress object to the function if necessary
        kwargs = self._add_job_progress_to_kwargs(route_function, job, kwargs)

        # check the arguments for the path function
        sig = inspect.signature(route_function)
        missing_args = [arg for arg in sig.parameters if arg not in kwargs]
        if len(missing_args) > 0:
            raise Exception(f"Arguments {missing_args} are missing")

        # handle file uploads
        kwargs = self._handle_file_uploads(route_function, **kwargs)

        # catch errors and display readable error messages
        try:
            return route_function(**kwargs)
        except Exception as e:
            raise Exception(f"Error in path {path}: {e}")

    def handler(self, job):
        """
        The handler function that is called by the runpod serverless framework.
        We wrap it to provide internal routing in the serverless framework.
        Args:
            job: the job that is passed by the runpod serverless framework. Must include "path" in the input.
        Returns: the result of the path function.
        """
        inputs = job["input"]
        if "path" not in inputs:
            raise Exception("No path provided")

        route = inputs["path"]
        del inputs["path"]

        return self._router(route, job, **inputs)

    def start_runpod_serverless_localhost(self, port):
        # add the -rp_serve_api to the command line arguments to allow debugging
        import sys
        sys.argv.append("--rp_serve_api")
        sys.argv.extend(["--rp_api_port", str(port)])

        # overwrite runpod variables. Little hacky but runpod does not expose the variables in a nice way.
        import runpod.serverless
        from runpod.serverless.modules import rp_fastapi
        rp_fastapi.TITLE = self.title + " " + rp_fastapi.TITLE
        rp_fastapi.DESCRIPTION = self.summary + " " + rp_fastapi.DESCRIPTION
        desc = '''\
                        In input declare your path as route for the function. Other parameters follow in the input as usual.
                        The FastTaskAPI router will use the path argument to route to the correct function declared with 
                        @task_endpoint(path="your_path").
                        { "input": { "path": "your_path", "your_other_args": "your_other_args" } }
                    '''
        rp_fastapi.RUN_DESCRIPTION = desc + "\n" + rp_fastapi.RUN_DESCRIPTION

        class WorkerAPIWithModifiedInfo(rp_fastapi.WorkerAPI):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._orig_openapi_func = self.rp_app.openapi
                self.rp_app.openapi = self.custom_openapi

            def custom_openapi(self):
                if not self.rp_app.openapi_schema:
                    self._orig_openapi_func()
                version = importlib.metadata.version("fast-task-api")
                self.rp_app.openapi_schema["info"]["fast-task-api"] = version
                self.rp_app.openapi_schema["info"]["runpod"] = rp_fastapi.runpod_version
                return self.rp_app.openapi_schema

        rp_fastapi.WorkerAPI = WorkerAPIWithModifiedInfo

        runpod.serverless.start({"handler": self.handler})

    def start(self, environment: Union[FTAPI_DEPLOYMENTS, str] = FTAPI_DEPLOYMENT, port=8000):
        if type(environment) is str:
            environment = FTAPI_DEPLOYMENTS(environment)

        if environment == environment.LOCALHOST:
            self.start_runpod_serverless_localhost(port=port)
        elif environment == environment.SERVERLESS:
            import runpod.serverless
            runpod.serverless.start({"handler": self.handler})
        else:
            raise Exception(f"Not implemented for environment {environment}")

