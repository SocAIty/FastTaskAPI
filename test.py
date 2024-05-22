import time

import fastapi

from socaity_router import SocaityRouter
from socaity_router import JobProgress
from socaity_router.compatibility.upload import UploadDataType
from socaity_router.settings import EXECUTION_PROVIDER

#router = SocaityRouter(provider="runpod")
router = SocaityRouter(
    provider=EXECUTION_PROVIDER,
    app=fastapi.FastAPI(
        title="Face2Face FastAPI",
        summary="Swap faces from images. Create face embeddings. Integrate into hosted environments.",
        version="0.0.1",
        contact={
            "name": "w4hns1nn",
            "url": "https://github.com/w4hns1nn",
        }),
)

@router.post(path="/predict", queue_size=10)
def predict(job_progress: JobProgress, my_param1: str, my_param2: int = 0, my_param3: UploadDataType.FILE = None):
    job_progress.set_status(0.1, "I am working on it")
    time.sleep(1)
    job_progress.set_status(0.5, "I am working on it")
    time.sleep(2)
    job_progress.set_status(0.8, "Still working on it. Almost done")
    time.sleep(2)
    return f"my_awesome_prediction {my_param1}"

@router.add_route(path="func1")
def func1(myarg1: int, myarg2):
    return "func1"

@router.add_route(path="func2")
def func2(myarg3: int, myarg2):
    return "func2"


if __name__ == "__main__":
    # Runpod version
    router.start(port=8000, environment="localhost")
    # router.start(environment="serverless", port=8000)
    # router.start(environment="localhost", port=8000)

