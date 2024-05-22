from socaity_router.CONSTS import EXECUTION_PROVIDERS
from socaity_router.settings import EXECUTION_PROVIDER
from socaity_router.core.routers._SocaityRouter import _SocaityRouter
from socaity_router.core.routers._runpod_router import SocaityRunpodRouter
from socaity_router.core.routers._fastapi_router import SocaityFastAPIRouter
from typing import Union

def SocaityRouter(
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

    router = class_map[provider](*args, **kwargs)
    # ToDo: add default endpoints status, get_job here instead of the subclasses
    #router.add_route(path="/status")(router.get_status)
    #router.add_route(path="/job")(router.get_job)

    return router
