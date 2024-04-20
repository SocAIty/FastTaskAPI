import sys
from os import environ

from socaity_router.CONSTS import EXECUTION_PROVIDERS, EXECUTION_ENVIRONMENTS

sys.argv.extend(['rp_serve_api', '1'])
sys.argv.extend(['--rp_serve_api', '1'])

# Set the execution mode
EXECUTION_ENVIRONMENT = environ.get("EXECUTION_ENVIRONMENT", EXECUTION_ENVIRONMENTS.LOCALHOST)
EXECUTION_PROVIDER = environ.get("EXECUTION_PROVIDER", EXECUTION_PROVIDERS.FASTAPI)


# to run the runpod serverless framework locally, the following two lines must be added
if EXECUTION_PROVIDER == EXECUTION_PROVIDER.RUNPOD and EXECUTION_ENVIRONMENT == EXECUTION_ENVIRONMENTS.LOCALHOST:
    sys.argv.extend(['--rp_serve_api', '1'])
