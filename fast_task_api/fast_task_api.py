from fast_task_api.CONSTS import FTAPI_BACKENDS, FTAPI_DEPLOYMENTS
from fast_task_api.settings import FTAPI_BACKEND
from fast_task_api.core.routers._socaity_router import _SocaityRouter
from fast_task_api.core.routers._runpod_router import SocaityRunpodRouter
from fast_task_api.core.routers._fastapi_router import SocaityFastAPIRouter
from typing import Union

def FastTaskAPI(
        backend: Union[FTAPI_BACKENDS, str] = None,
        deployment: Union[FTAPI_DEPLOYMENTS, str] = None,
        host: str = "0.0.0.0",
        *args, **kwargs
) -> Union[_SocaityRouter, SocaityRunpodRouter, SocaityFastAPIRouter]:
    """
    Initialize a _SocaityRouter with the appropriate backend running in the specified environment
    This function is a factory function that returns the appropriate app based on the backend and environment
    Args:
        backend: fastapi, runpod
        deployment: localhost, serverless
        host: The host to run the uvicorn host on.
        *args:
        **kwargs:

    Returns: _SocaityRouter
    """
    if backend is None:
        backend = FTAPI_BACKEND

    class_map = {
        FTAPI_BACKENDS.FASTAPI: SocaityFastAPIRouter,
        FTAPI_BACKENDS.RUNPOD: SocaityRunpodRouter
    }

    backend = FTAPI_BACKENDS(backend) if type(backend) is str else backend

    if backend not in class_map:
        raise Exception(f"Backend {backend.value} not found")

    if deployment is None:
        deployment = FTAPI_DEPLOYMENTS.LOCALHOST

    deployment = FTAPI_DEPLOYMENTS(deployment) if type(deployment) is str else deployment

    print(f"Starting fast-task-api with backend {backend} in deployment mode {deployment}")
    backend_instance = class_map[backend](deployment=deployment, host=host, *args, **kwargs)
    # ToDo: add default endpoints status, get_job here instead of the subclasses
    #app.add_route(path="/status")(app.get_status)
    #app.add_route(path="/job")(app.get_job)

    return backend_instance
