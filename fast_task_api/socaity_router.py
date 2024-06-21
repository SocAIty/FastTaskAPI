from fast_task_api.CONSTS import EXECUTION_PROVIDERS
from fast_task_api.settings import EXECUTION_PROVIDER
from fast_task_api.core.routers._SocaityRouter import _SocaityRouter
from fast_task_api.core.routers._runpod_router import SocaityRunpodRouter
from fast_task_api.core.routers._fastapi_router import SocaityFastAPIRouter
from typing import Union

def FastTaskAPI(
        provider: Union[EXECUTION_PROVIDERS, str] = None,
        *args, **kwargs
) -> Union[_SocaityRouter, SocaityRunpodRouter, SocaityFastAPIRouter]:
    """
    Initialize a _SocaityRouter with the appropriate provider running in the specified environment
    This function is a factory function that returns the appropriate router based on the provider and environment
    Args:
        provider: fastapi, runpod
        environment: localhost, serverless
        *args:
        **kwargs:

    Returns: _SocaityRouter
    """
    if provider is None:
        provider = EXECUTION_PROVIDER

    class_map = {
        EXECUTION_PROVIDERS.FASTAPI: SocaityFastAPIRouter,
        EXECUTION_PROVIDERS.RUNPOD: SocaityRunpodRouter
    }

    provider = EXECUTION_PROVIDERS(provider) if type(provider) is str else provider

    if provider not in class_map:
        raise Exception(f"Provider {provider.value} not found")

    backend_instance = class_map[provider](*args, **kwargs)
    # ToDo: add default endpoints status, get_job here instead of the subclasses
    #router.add_route(path="/status")(router.get_status)
    #router.add_route(path="/job")(router.get_job)

    return backend_instance
