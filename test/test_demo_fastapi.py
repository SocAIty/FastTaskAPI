import fastapi
from fast_task_api import FastTaskAPI
from fast_task_api import JobProgress
from fast_task_api.settings import EXECUTION_PROVIDER
from fast_task_api import ImageFile
import time
import numpy as np

# define the app including your provider (fastapi, runpod..)
app = FastTaskAPI(
    #provider=EXECUTION_PROVIDER,
    #app=fastapi.FastAPI(
    #    title="Img2Img",
    #    summary="Super good image to image conversion",
    #    version="0.0.1",
    #    contact={
    #        "name": "w4hns1nn",
    #        "url": "https://github.com/w4hns1nn",
    #    }),
)

# add endpoints to your service
@app.task_endpoint("/predict")
def predict(my_param1: str, my_param2: int = 0):
    return f"my_awesome_prediction {my_param1} {my_param2}"

@app.task_endpoint("/img2img")
def img2img(upload_img: ImageFile):
    img_as_numpy = np.array(upload_img)  # this returns a np.array read with cv2
    # Do some hard work here...
    # img_as_numpy = img2img(img_as_numpy)
    return ImageFile().from_np_array(img_as_numpy)

@app.get(path="/prompt_helper", queue_size=100)
def prompt_helper(job_progress: JobProgress, text: str, enhancement: int = 1):
    """
    Submit a prompt and we will improve its quality to make the best out of your images.
    :return: a super enhanced prompt
    """
    job_progress.set_status(0.1, f"enhancing your prompt with fancy addons like 8k, ultra high res")
    time.sleep(1)
    text += " 8k, ultra high res, perfect anatomy"
    job_progress.set_status(0.5, f"I am working on it. Lots of work to do {enhancement}")
    time.sleep(2)
    job_progress.set_status(0.8, "Still working on it. Almost done")
    time.sleep(2)
    return f"Your enhanced prompt {text} is ready"

# start and run the server
app.start()