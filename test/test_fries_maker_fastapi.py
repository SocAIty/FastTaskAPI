import time
import fastapi
from fastapi import UploadFile as fastapiUploadFile
from fast_task_api import FastTaskAPI
from fast_task_api import JobProgress
from fast_task_api import MultiModalFile, ImageFile, AudioFile, VideoFile

#app = SocaityRouter(provider="runpod")
router = FastTaskAPI(
    app=fastapi.FastAPI(
        title="FriesMaker",
        summary="Make fries from potatoes",
        version="0.0.1",
        contact={
            "name": "SocAIty",
            "url": "https://github.com/SocAIty",
        }),
)

@router.post(path="/make_fries", queue_size=10)
def make_fries(job_progress: JobProgress, fries_name: str, amount: int = 1):
    job_progress.set_status(0.1, f"started new fries creation {fries_name}")
    time.sleep(1)
    job_progress.set_status(0.5, f"I am working on it. Lots of work to do {amount}")
    time.sleep(2)
    job_progress.set_status(0.8, "Still working on it. Almost done")
    time.sleep(2)
    return f"Your fries {fries_name} are ready"


@router.task_endpoint("/make_file_fries")
def make_fries_from_files(
        potato_one: MultiModalFile,
        potato_two: fastapiUploadFile,
    ):
    potato_one_content = potato_one.to_bytes()

    return "fries"

@router.task_endpoint("/make_image_fries")
def make_image_fries(potato_one: ImageFile):
    data1 = potato_one.to_cv2_img()
    print(f"recieved data {data1.shape}")
    return f"image fries {data1.shape}"


@router.task_endpoint("/make_audio_fries")
def make_audio_fries(
        potato_one: MultiModalFile,
        potato_two: AudioFile,
    ):

    potato_one_content = potato_one.to_bytes()
    potato_two_content = potato_two.to_np_array()

    return "audio_fries"

@router.task_endpoint("/make_video_fries")
def make_video_fries(
        potato_one: MultiModalFile,
        potato_two: VideoFile,
    ):
    potato_one_content = potato_one.content
    potato_two_content = potato_two.content
    return "video_fries"


if __name__ == "__main__":
    # Runpod version
    router.start(port=8000, environment="localhost")
    # app.start(environment="serverless", port=8000)
    # app.start(environment="localhost", port=8000)

