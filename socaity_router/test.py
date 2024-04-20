# your_handler.py
import uvicorn
from fastapi import FastAPI

from socaity_router.sai_router import SocaityRouter

# router = SocaityRouter(provider="runpod", environment="localhost")
router = SocaityRouter(provider="fastapi", environment="localhost")

@router.add_route(path="func1")
def func1(myarg1: int, myarg2):
    return "func1"

@router.add_route(path="func2")
def func2(myarg3: int, myarg2):
    return "func2"


if __name__ == "__main__":
    import uvicorn
    app = FastAPI()
    app.include_router(router, prefix="/api")
    uvicorn.run(app, host="localhost", port=8000)

# router.start()

#import runpod  # Required.
#
#def handler(job):
#    job_input = job["input"]  # Access the input from the request.
#    # Add your custom code here.
#    return "Your job results"
#
#def handler2(job2):
#    job_input = job2["input"]  # Access the input from the request.
#    # Add your custom code here.
#    return "Your job results2"
#
#
#runpod.serverless.start({"handler": handler})  # Required.