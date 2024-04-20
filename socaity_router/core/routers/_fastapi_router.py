from fastapi import APIRouter
from socaity_router.CONSTS import SERVER_STATUS
from socaity_router.core.JobQueue import JobQueue
from socaity_router.core.routers.router_mixins._queue_mixin import _QueueMixin


class SocaityFastAPIRouter(APIRouter, _QueueMixin):

    def __init__(self):
        #super(APIRouter, self).__init__()
        #super(_QueueMixin, self).__init__()
        super().__init__()
        self.job_queue = JobQueue()
        self.status = SERVER_STATUS.INITIALIZING

        # add the get_status function to the routes
        # self.add_api_route(path="/status")

    def get_status(self):
        jobs_status = self.job_queue.get_status()
        return self.status

    def start_func(self, *args, **kwargs):
        """Decorator for subclasses to use like @start_func"""

        def wrapper(s_func):
            self.status = SERVER_STATUS.BOOTING
            s_func(*args, **kwargs)
            self.status = SERVER_STATUS.RUNNING

        return wrapper

    def start_func_serverless(self, *args, **kwargs):
        """Decorator for subclasses to use like @start_func_serverless"""

        def wrapper(s_func):
            self.status = SERVER_STATUS.BOOTING
            s_func(*args, **kwargs)
            self.status = SERVER_STATUS.RUNNING

        return wrapper

    def add_route(
            self,
            path: str,
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
        if len(path) > 0 and path[0] != "/":
            path = "/" + path

        fastapi_route_decorator_func = self.api_route(
            path=path,
            methods=["POST"],
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
            return fastapi_route_decorator_func(queue_router_decorator_func(func))

        return decorator



#class SocaityFastAPIRouter(APIRouter, _SocaityRouter):
#
#    def api_route(
#        self,
#        path: str = None,
#        *args,
#        **kwargs
#    ):
#        """
#        Adds an additional wrapper to the API path to add functionality like:
#        - Add api key validation
#        - Create a job and add to the job queue
#        - Return job
#        """
#
#        fastapi_route_decorator_func = super().api_route(
#            path,
#            *args,
#            **kwargs
#        )
#
#        def decorator(func):
#            # With this wrapper we create the job while execution and add it to the job queue.
#            @functools.wraps(func)
#            def wrapper(*wrapped_func_args, **wrapped_func_kwargs) -> JobResult:
#                ## Get the parameters of the original function
#                #func_params = inspect.signature(func).parameters
##
#                ## Add the new parameter to the wrapper's signature
#                #new_params = list(func_params.values()) + [
#                #    inspect.Parameter("provider", inspect.Parameter.KEYWORD_ONLY, default=None)]
#                #new_signature = inspect.Signature(new_params)
##
#                ## Bind the arguments to the new signature
#                #bound_args = new_signature.bind(*args, **kwargs)
#                #bound_args.apply_defaults()
#
#
#                print("decorator before")
#                ret = func(*wrapped_func_args, **wrapped_func_kwargs)
#                print("decorator after")
#                return ret
#
#                # Get the original function's signature
#
#            # Get the original function's signature
#            #orig_sig = inspect.signature(func)
##
#            ## Construct parameters for the new signature
#            #new_params = list(orig_sig.parameters.values())
#            #new_params.append(inspect.Parameter("provider", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None))
##
#            ## orig_sig.parameters["provider"] = inspect.Parameter("provider", inspect.Parameter.KEYWORD_ONLY, default=None)
#            ##new_params = []
#            ##for name, param in orig_sig.parameters.items():
#            ##    new_params.append(param)
#            ##    if param.kind == inspect.Parameter.VAR_POSITIONAL:
#            ##        new_params.append(inspect.Parameter("provider", inspect.Parameter.KEYWORD_ONLY, default=None))
###
#            ### Construct a new signature for the wrapper function
#            #wrapper_sig = orig_sig.replace(parameters=new_params)
##
#            ## Update the wrapper function's signature
#            #wrapper.__signature__ = wrapper_sig
#
#            return fastapi_route_decorator_func(wrapper)
#
#        return decorator
#
#    def get(
#        self,
#        path: str = None,
#        provider: str = None,
#        runpod_endpoint_id: str = None,
#        replicate_model_name: str = None,
#        *args,
#        **kwargs
#    ):
#        return self.api_route(
#            path=path,
#            provider=provider,
#            runpod_endpoint_id=runpod_endpoint_id,
#            replicate_model_name=replicate_model_name,
#            methods=["GET"],
#            *args,
#            **kwargs
#        )