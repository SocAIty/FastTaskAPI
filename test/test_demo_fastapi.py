import fastapi
from fast_task_api import FastTaskAPI
from fast_task_api import JobProgress
from fast_task_api.settings import EXECUTION_PROVIDER
from fast_task_api import ImageFile
import time
import numpy as np

router = FastTaskAPI(
    provider=EXECUTION_PROVIDER,
    app=fastapi.FastAPI(
        title="Best AI service ever",
        summary="Make predictions and fries",
        version="0.0.1",
        contact={
            "name": "w4hns1nn",
            "url": "https://github.com/w4hns1nn",
        }),
)

# define the router including your provider (fastapi, runpod..)
router = FastTaskAPI()

# add endpoints to your service
@router.add_route("/predict")
def predict(my_param1: str, my_param2: int = 0):
    return f"my_awesome_prediction {my_param1} {my_param2}"

@router.add_route("/img2img")
def my_image_manipulator(upload_img: ImageFile):
    img_as_numpy = np.array(upload_img)  # this returns a np.array read with cv2
    # Do some hard work here...
    # img_as_numpy = img2img(img_as_numpy)
    return ImageFile().from_np_array(img_as_numpy)

@router.post(path="/make_fries", queue_size=100)
def make_fries(job_progress: JobProgress, fries_name: str, amount: int = 1):
    job_progress.set_status(0.1, f"started new fries creation {fries_name}")
    time.sleep(1)
    job_progress.set_status(0.5, f"I am working on it. Lots of work to do {amount}")
    time.sleep(2)
    job_progress.set_status(0.8, "Still working on it. Almost done")
    time.sleep(2)
    return f"Your fries {fries_name} are ready"

# start and run the server
router.start()