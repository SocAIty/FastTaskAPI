import functools
import inspect

from socaity_router.CONSTS import SERVER_STATUS
from socaity_router.core.routers._SocaityRouter import _SocaityRouter


class SocaityRunpodRouter(_SocaityRouter):
    """
    Adds routing functionality for the runpod serverless framework.
    The runpod_handler has an additional argument "path" which is the path to the function.
    Implementation is inspired by the fastapi router.
    """
    def __init__(self):
        super().__init__()
        self.routes = {}   # routes are organized like {"ROUTE_NAME": "ROUTE_FUNCTION"}

    def add_route(
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

    def _router(self, path, **kwargs):
        if len(path) > 0 and path[0] == "/":
            path = path[1:]

        route_function = self.routes.get(path, None)
        if route_function is None:
            raise Exception(f"Route {path} not found")

        # check the arguments for the path function
        sig = inspect.signature(route_function)
        missing_args = [arg for arg in sig.parameters if arg not in kwargs]
        if len(missing_args) > 0:
            raise Exception(f"Arguments {missing_args} are missing")

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

        return self._router(route, **inputs)

    def serverless_start(self):
        import runpod.serverless
        runpod.serverless.start({"handler": self.handler})

    def start(self):
        self.serverless_start()




