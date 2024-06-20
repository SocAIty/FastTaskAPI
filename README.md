
  <h1 align="center" style="margin-top:-25px">SOC<span style="color: #a0d802">AI</span>TY ROUTER</h1>
  <h3 align="center" style="margin-top:-10px">Create web-APIs for long-running tasks</h3>
<p align="center">
  <img align="center" src="docs/socaity_router_icon.png" height="200" />
</p>

<p align="center">
Create a job and return a job id. Get the result with the job id later.</br>
Socaity router creates threaded jobs and job queues on the fly.</br>
Run services anywhere, be it local, hosted or serverless.</br>
</p>


We developed socaity router to create and deploy our AI services as easy and standardized as possible.
Built on-top of FastAPI and runpod you can built high quality endpoints with proven stability. 






## Table of contents

Introduction
- [Why is this useful?](#why-is-this-useful): A section explaining why you should use this package.
- [What does this do?](#what-does-this-do): A section explaining the features of this package.

Get started:
- [Installation](#installation): A section explaining how to install the package.
- [First-steps](#how-to-use): Create your first service with the socaity router.



## Why is this useful?
Creating AI services is hard.
- The inference time makes realtime results difficult. Parallel jobs, and a Job queue is often required. For example as a client you would not like to wait for a server response instead do some work until the server produced the result.
- Serverless deployments like runpod often DO NOT provide routing functionality. This router works in this conditions.
- Scaling AI services is hard.
- Streaming services (for example for generative models) is complicated to setup.


This package solves these problems, by providing a simple well-known interface to deploy AI services anywhere.</br>
The syntax is oriented by the simplicity of fastapi. Other hazards are taken care of by our router.


<img align="right" src="docs/socaity_services.png" height="500" style="margin-left:-10px; margin-top: -10px" />

## What does this do?

- Routing functionality: for serverless providers like [Runpod](Runpod.io)
- Jobs, job queues for your service (no code required).
- Async, sync and streaming functionality.
  - Including progress bars.
- File support, also for serverless providers like [Runpod](https://docs.runpod.io/serverless/workers/handlers/overview) 
  - Simplified sending files to the service with socaity-client 
  - One line file response with [multimodal-files](https://github.com/SocAIty/multimodal-files) including images, audio, video and more.
- Integration: integrates neatly into the SOCAITY ecosystem for running AI services like python functions with our [Client](https://github.com/SocAIty/socaity-client)/[SDK](https://github.com/SocAIty/socaity).
- Monitoring server state.

The code is fast, lightweight, flexible and pure python.

## Installation 
You can install the package with PIP, or clone the repository.
Install the package with pip from the github repository.

```python
pip install git+git://github.com/SocAIty/socaity_router
```
We will release a pypi package as soon as the first version is stable.


# How to use
## Create your first service
Use the decorator syntax @router.add_route to add a route. This syntax is similar to [fastapi](https://fastapi.tiangolo.com/tutorial/first-steps/)'s @app.get syntax.

```python
from socaity_router import SocaityRouter, ImageFile

# define the router including your provider (fastapi, runpod..)
router = SocaityRouter() 

# add endpoints to your service
@router.add_route("/predict")
def predict(my_param1: str, my_param2: int = 0):
    return f"my_awesome_prediction {my_param1} {my_param2}"

@router.add_route("/img2img")
def my_image_manipulator(upload_img: ImageFile):
    img_as_numpy = np.array(upload_img)  # this returns a np.array read with cv2
    my_manipulated_image = my_image_manipulator(img_as_numpy)
    return ImageFile.from_numpy_array(my_manipulated_image)

# start and run the server
router.start()
```


Set environment variables to determine the deployment target or provide the values in the constructor.
Default is ```EXECUTION_ENVIORNMENT="localhost"``` and ```EXECUTION_PROVIDER="fastapi"```.
Possible values are ```"local"```, ```"serverless"```, ```"hosted"```, ```"decentralized"``` and ```"fastapi"```, ```"runpod"```

To deploy multiple methods for a serverless provider like Runpod simply set the environment variable ```EXECUTION_PROVIDER="runpod"```.
Or use the constructor to set the provider.

```python
SocaityRouter(provider="fastapi")
```
To deploy to runpod all you have to do is to write a simple docker file to deploy the service. 
No custom handler writing is required.


## Jobs and job queues

If you have a long running task, you can use the job queue functionality. 
```python
@router.post(path="/make_fries", queue_size=100)
def make_fries(job_progress: JobProgress, fries_name: str, amount: int = 1):
    job_progress.set_status(0.1, f"started new fries creation {fries_name}")
    time.sleep(1)
    job_progress.set_status(0.5, f"I am working on it. Lots of work to do {amount}")
    time.sleep(2)
    job_progress.set_status(0.8, "Still working on it. Almost done")
    time.sleep(2)
    return f"Your fries {fries_name} are ready"
```
What will happen now is: 
- The method will return a "Job" object instead of the result, including a job id. This json is send back to the client.
- By calling the status endpoint with status?job_id=... one gets the result / status of the job.

Note: in case of "runpod", "serverless" this is not necessary, as the job mechanism is handled by runpod deployment.

## Calling the endpoints -> Getting the job result

You can call the endpoints with a simple http request.
You can try them out in the browser, with curl or Postman. 
For more convenience with the socaity package, you can use the endpoints like functions.

## Use the endpoints like functions with the socaity client.
If you have the socaity package installed, you can use the endpoints like a function.
This makes it insanely useful for complex scenarious where you use multiple models and endpoints.
Socaity package release comes soon.

#### Async

After you added your service_client to the SDK, you can call the endpoints like functions.
Check-out the socaity package for more information.

```python
f2f = face2face()
job = f2f.swap_one_from_file("test", target_img="test")
job.run()
result = job.wait_for_result()
```
#### Run sync
If you want to run the endpoint sync, you can add ?sync=true to the endpoint, to wait for the result.
Then the server will wait with a response until the job is finished.



### Job status and progress bars

You can provide status updates by changing the values of the job_progress object. 
If you add a parameter named job_progress to the function we will pass that object to the function.
If then a client asks for the status of the task, he will get the messages and the process bar. This is for example in the socaity package used to provide a progress bar.

```python
@SocaityRouter.add_route("/predict", queue_size=10)
def predict(job_progress: JobProgress, my_param1: str, my_param2: int = 0):
    job_progress._message = "I am working on it"
    job_progress._progress = 0.5
    job_progress._message = "Still working on it. Almost done"
    job_progress._progress = 0.8
    return "my_awesome_prediction"
```
When the return is finished, the job is marked as done and the progress bar is automatically set to 1.


### File uploads and files.

The library supports file uploads out of the box. 
Use the parameter type hints in your method definition to get the file.

```python
from socaity_router import MultiModalFile, ImageFile, AudioFile, VideoFile


def my_upload(anyfile: MultiModalFile):
    return anyfile.content
```
We have specializations for ImageFile, AudioFile and VideoFile.
```python
from socaity_router import ImageFile, AudioFile, VideoFile
def my_upload_image(image: ImageFile, audio: AudioFile, video: VideoFile):
    return image.content
```

Note that for using these files you also need to install other dependencies.
For ImageFile you will need `opencv-python`, for AudioFile `librosa` and for VideoFile `moviepy`.
If you want to install those dependencies easily run `pip install -r requirements_uploadfiles.txt`.

You can call the endpoints, either with bytes or b64 encoded strings. 
If you call the endpoint with the socaity-client it converts it for you automatically.



# Deploying a Service to production

## Runpod
It is not required to write a [handler](https://docs.runpod.io/serverless/workers/handlers/overview) function anymore. The socaity router magic handles it :D
Just write a simple docker file and deploy it to runpod. 

## Locally
Just run the server. He is compatible with the socaity package.

## Writing your own Router

You can also write your own router to extend the SocaityRouters capabilities.


## Note: THE PACKAGE IS STILL IN DEVELOPMENT!
#### LEAVE A STAR TO SUPPORT US. ANY BUG REPORT OR CONTRIBUTION IS HIGHLY APPRECIATED.
