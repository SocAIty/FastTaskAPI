from CONSTS import EXECUTION_PROVIDERS, EXECUTION_ENVIRONMENTS
from settings import EXECUTION_PROVIDER, EXECUTION_ENVIRONMENT
from socaity_router.core.routers._SocaityRouter import _SocaityRouter
from socaity_router.core.routers._runpod_router import SocaityRunpodRouter
from socaity_router.core.routers._fastapi_router import SocaityFastAPIRouter
from typing import Union

def SocaityRouter(
        provider: Union[EXECUTION_PROVIDERS, str] = None,
        environment: Union[EXECUTION_ENVIRONMENTS, str] = None, *args, **kwargs) \
        -> Union[_SocaityRouter, SocaityRunpodRouter, SocaityFastAPIRouter]:
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
    if environment is None:
        environment = EXECUTION_ENVIRONMENT

    class_map = {
        EXECUTION_PROVIDERS.FASTAPI: SocaityFastAPIRouter,
        EXECUTION_PROVIDERS.RUNPOD: SocaityRunpodRouter
    }

    provider = EXECUTION_PROVIDERS(provider) if type(provider) is str else provider
    environment = EXECUTION_ENVIRONMENTS(environment) if type(environment) is str else environment

    if provider not in class_map:
        raise Exception(f"Provider {provider.value} not found")

    return class_map[provider](*args, **kwargs)
