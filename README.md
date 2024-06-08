# SOCAITY ROUTER

A router for AI services running anywhere, locally, hosted, serverless and decentralized.
Plays well with existing providers like runpod and famous libraries like fastapi.

### PACKAGE IS IN DEVELOPMENT!
#### LEAVE A STAR TO SUPPORT US AN TO GET NOTIFIED WHEN THE PACKAGE IS RELEASED.
We will release a pypi package as soon as the first version is stable.
Until then you can clone / fork the repository or install the package with pip from the github repository.

```python
pip install git+git://github.com/SocAIty/socaity_router
```

## Why is this useful?
Deploying AI services is hard. 
- Serverless deployments like runpod often DO NOT provide routing functionality.
- The inference time makes realtime results difficult. Parallel jobs, and a Job queue is often required. 
- Scaling AI services is hard.
- Streaming services (for example for generative models) is complicated to setup.


This package solves these problems, by providing a simple well-known interface to deploy AI services anywhere.
The syntax is oriented by the simplicity of fastapi. Other hazards are taken care of by our router.

## What does this do?

- Routing functionality for serverless providers like [Runpod](Runpod.io)
- Adding jobs, job queues for your service (no code required)
- Providing async, sync and streaming functionality.
  - Including progress bars.
- Native fastapi like file-uploads for serverless providers like [Runpod](https://docs.runpod.io/serverless/workers/handlers/overview) 
  - Simplified usage of ImageFile, AudioFile, VideoFile
- Neat less integration into the SOCAITY ecosystem for running AI services like python functions with our Client/SDK.
- Monitoring server state.

The code is fast, lightweight, flexible and pure python.

# How to use
Just use the known syntax of fastapi to define your routes.

```python
from socaity_router import SocaityRouter

router = SocaityRouter(provider="runpod", environment="localhost")

@SocaityRouter.add_route("/predict")
def predict(my_param1: str, my_param2: int = 0):
    return "my_awesome_prediction"

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

If you have a long running task, you can use the job queue functionality. By default, the queue size is 100.
```python
@SocaityRouter.add_route("/predict", queue_size=100)
def predict(my_param1: str, my_param2: int = 0):
    time.sleep(10) # heavy computation
    return "my_awesome_prediction"
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
from socaity_router import UploadFile, ImageFile, AudioFile, VideoFile
def my_upload(anyfile: UploadFile):
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
