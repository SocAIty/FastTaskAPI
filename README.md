
  <h1 align="center" style="margin-top:-25px">FastTaskAPI</h1>
  <h3 align="center" style="margin-top:-10px">Create web-APIs for long-running tasks</h3>
<p align="center">
  <img align="center" src="docs/socaity_router_icon.png" height="200" />
</p>

<p align="center">
Call the server and return a job id. Get the result with the job id later.</br>
FastTaskAPI creates threaded jobs and job queues on the fly.</br>
Run services anywhere, be it local, hosted or serverless.</br>
</p>

<p align="center">
We at SocAIty developed FastTaskAPI to create and deploy our AI services as easy and standardized as possible.
Built on-top of FastAPI and runpod you can built high quality endpoints with proven stability. 
</p>

## Table of contents

Introduction
- [Why is this useful?](#why-is-this-useful): A section explaining why you should use this package.
- [What does this do?](#what-does-this-do): A section explaining the features of this package.

Get started:
- [Installation](#installation): A section explaining how to install the package.
- [First-steps](#how-to-use): Create your first service with the socaity router.
- [Jobs and job queues](#jobs-and-job-queues): A section explaining how to use the job queue functionality.
- [File uploads and files](#file-uploads-and-files): A section explaining how to use file uploads and files.
- [Backends and deploying a service](#backends-and-deploying-a-service): Deploy serverless for example with runpod.


## Why is this useful?
Creating services for long-running tasks is hard.
- In AI services inference time makes realtime results difficult. Parallel jobs, and a Job queue is often required. For example as a client you would not like to wait for a server response instead do some work until the server produced the result.
- Serverless deployments like runpod often DO NOT provide routing functionality. This router works in this conditions.
- Scaling AI services is hard.
- Streaming services (for example for generative models) is complicated to setup.


This package solves these problems, by providing a simple well-known interface to deploy AI services anywhere.</br>
The syntax is oriented by the simplicity of fastapi. Other hazards are taken care of by our router.


## What does this do?
<img align="right" src="docs/socaity_services.png" height="400" style="margin-top: 50px" />


- Jobs, job queues for your service (no code required).
- Routing functionality: for serverless providers like [Runpod](Runpod.io)
- Async, sync and streaming functionality.
  - Including progress bars.
- File support, also for serverless providers like [Runpod](https://docs.runpod.io/serverless/workers/handlers/overview) 
  - Simplified sending files to the services with [fastSDK](https://github.com/SocAIty/fastSDK) 
  - One line file response with [multimodal-files](https://github.com/SocAIty/multimodal-files) including images, audio, video and more.
- Integration: integrates neatly into the SOCAITY ecosystem for running AI services like python functions with our [Client](https://github.com/SocAIty/socaity-client)/[fastSDK](https://github.com/SocAIty/socaity).
- Monitoring server state.

The code is fast, lightweight, flexible and pure python.

## Installation 
You can install the package with PIP, or clone the repository.

```python
# install from pypi
pip install fast-task-api
# install from github for the newest version
pip install git+git://github.com/SocAIty/FastTaskAPI
```

# How to use
## Create your first service
Use the decorator syntax @app.task_endpoint to add an endpoint. This syntax is similar to [fastapi](https://fastapi.tiangolo.com/tutorial/first-steps/)'s @app.get syntax.

```python
from fast_task_api import FastTaskAPI, ImageFile

# define the app including your provider (fastapi, runpod..)
app = FastTaskAPI()

# add endpoints to your service
@app.task_endpoint("/predict")
def predict(my_param1: str, my_param2: int = 0):
  return f"my_awesome_prediction {my_param1} {my_param2}"

@app.task_endpoint("/img2img", queue_size=10)
def my_image_manipulator(upload_img: ImageFile):
  img_as_numpy = upload_img.to_np_array() 
  # Do some hard work here...
  # img_as_numpy = img2img(img_as_numpy)
  return ImageFile().from_np_array(img_as_numpy)

# start and run the server
app.start()
```
If you execute this code you should see the following page under http://localhost:8000/docs.
<img align="center" src="docs/demo_service.png" />

## Jobs and job queues

If you have a long running task, you can use the job queue functionality. 
```python
@app.task_endpoint(path="/make_fries", queue_size=100)
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

### Calling the endpoints -> Getting the job result

You can call the endpoints with a simple http request.
You can try them out in the browser, with curl or Postman. 
For more convenience with the socaity package, you can use the endpoints like functions.

### Use the endpoints like functions with [fastSDK](https://github.com/SocAIty/fastSDK).
With fastSDK, you can use the endpoints like a function. FastSDK will deal with the job id and the status requests in the background.
This makes it insanely useful for complex scenarios where you use multiple models and endpoints.

### Job status and progress bars

You can provide status updates by changing the values of the job_progress object. 
If you add a parameter named job_progress to the function we will pass that object to the function.
If then a client asks for the status of the task, he will get the messages and the process bar. This is for example in the socaity package used to provide a progress bar.

```python
@app.task_endpoint("/predict", queue_size=10)
def predict(job_progress: JobProgress, my_param1: str, my_param2: int = 0):
  job_progress._message = "I am working on it"
  job_progress._progress = 0.5
  job_progress._message = "Still working on it. Almost done"
  job_progress._progress = 0.8
  return "my_awesome_prediction"
```
When the return is finished, the job is marked as done and the progress bar is automatically set to 1.


### Normal openapi (no-task) endpoints

If you don't want to use the job queue functionality, you can use the ```@app.endpoint``` syntax
```python
@app.endpoint("/my_normal_endpoint", methods=["GET", "POST"]):
def my_normal_endpoint(image: str, my_param2: int = 0):
  return f"my_awesome_prediction {my_param1} {my_param2}"
```
This will return a regular endpoint -> No job_result object with job-id is returned.
The method also supports file uploads.

## File uploads and files.

The library supports file uploads out of the box. 
Use the parameter type hints in your method definition to get the file.

```python
from fast_task_api import MultiModalFile, ImageFile, AudioFile, VideoFile

def my_upload(anyfile: MultiModalFile):
    return anyfile.content
```
FastTaskAPI supports all file-types of [multimodal-files](https://github.com/SocAIty/multimodal-files). This includes common file types like: ImageFile, AudioFile and VideoFile.
```python
from fast_task_api import ImageFile, AudioFile, VideoFile
def my_upload_image(image: ImageFile, audio: AudioFile, video: VideoFile):
    image_as_np_array = np.array(image)
```
You can call the endpoints, either with bytes or b64 encoded strings. 

### Sending requests (and files) to the service with FastSDK

FastSDK also natively support mutlimodal-files and for this reason it natively supports file up/downloads.
Once you have added the service in FastSDK you can call it like a python function
```
mysdk = mySDK() # follow the fastSDK tutorial to set up correctly.
task = upload_image(my_imageFile, myAudioFile, myVideoFile) # uploads the data to the service. Retrieves a job back.
result = task.get_result()  # constantly trigger the get_job endpoint in the background until the server finished.
```

### Sending files to the service with httpx / requests

```python
import httpx
with open('my_image_file.png', 'rb') as f:
    image_file_content = f.read()

my_files = {
  "image": ("file_name", image_file_content, 'image/png')
  ...
}
response = httpx.Client().post(url, files=my_files)
```
Note: In case of runpod you need to convert the file to a b64 encoded string.

# Backends and deploying a service

You can change the provider either by setting it in the constructor or by setting the environment variable ```EXECUTION_PROVIDER="runpod"```.

## Runpod
To deploy multiple methods for a serverless provider like Runpod simply set the environment variable ```EXECUTION_PROVIDER="runpod"```.
Or use the constructor to set the provider.

```python
router = SocaityRouter(provider="runpod")
```
Set environment variables to determine the deployment target or provide the values in the constructor.
Default is ```EXECUTION_ENVIORNMENT="localhost"``` and ```EXECUTION_PROVIDER="fastapi"```.
Possible values are ```"local"```, ```"serverless"```, ```"hosted"```, ```"decentralized"``` and ```"fastapi"```, ```"runpod"```

To deploy to runpod all you have to do is to write a simple docker file to deploy the service. 
No custom handler writing is required.


## Runpod
It is not required to write a [handler](https://docs.runpod.io/serverless/workers/handlers/overview) function anymore. The socaity router magic handles it :D
Just write a simple docker file and deploy it to runpod. 


## Locally
Just run the server. He is compatible with the socaity package.


# Related projects and its differences

## Starlette Background Tasks

The fastapi documentation recommends using starlette background tasks for long-running tasks like sending an e-mail.
- No common interface / response type. 
  - This leads to re-implementing the same functionality over and over again.
  - Creates more overhead in the client and server code.
- No job progress and monitoring functionality
  - With background tasks clients have no chance to monitor the progress of the job or to know when the job is finished.
- No job queue:
  - If you don't have a job queue, the server can be overloaded with tasks pretty fast.
  - With socaity you can specify the maximum queue size for a task. If this is exceeded the task is not executed.

This is a good solution for simple tasks, but it does not provide a job queue or job status.


## Celery

Celery is a great tool for running jobs in the background on distributed systems.
However it comes with several drawbacks: 
- Hard to setup
- Doesn't run everywhere
- Overkill for most projects.

Socaity router is lightweight and provides background task functionality abstracted from the developer.
This doesn't mean that we don't recommend celery. Indeed it is planned to integrate celery as possible backend.


# Roadmap

- [x] stabilize runpod deployment
- [x] streaming support
- [x] add async functionality for fastapi
- [x] support other job-quing systems like celery


## Note: THE PACKAGE IS STILL IN DEVELOPMENT!
#### LEAVE A STAR TO SUPPORT US. ANY BUG REPORT OR CONTRIBUTION IS HIGHLY APPRECIATED.
