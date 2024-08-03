import sys
from os import environ
from fast_task_api.CONSTS import FTAPI_BACKENDS, FTAPI_DEPLOYMENTS

# Set the execution mode
FTAPI_DEPLOYMENT = environ.get("FTAPI_DEPLOYMENT", FTAPI_DEPLOYMENTS.LOCALHOST)
FTAPI_BACKEND = environ.get("FTAPI_BACKEND", FTAPI_BACKENDS.FASTAPI)

# to run the runpod serverless framework locally, the following two lines must be added
if FTAPI_BACKEND == FTAPI_BACKENDS.RUNPOD and FTAPI_DEPLOYMENT == FTAPI_DEPLOYMENTS.LOCALHOST:
    sys.argv.extend(['rp_serve_api', '1'])
    sys.argv.extend(['--rp_serve_api', '1'])

