# SOCAITY ROUTER

A router for AI services running anywhere, locally, hosted, serverless and decentralized.
Plays well with existing providers like runpod and famous libraries like fastapi.

### PACKAGE IS IN DEVELOPMENT
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
- Streaming (for example for generative models) is complicated to setup.


This package solves these problems, by providing a simple well-known interface to deploy AI services anywhere.
The syntax is oriented by the simplicity of fastapi. Other hazards are taken care of by our router.

## What does this do?

- Routing functionality for serverless providers like [Runpod](Runpod.io)
- Adding jobs, job queues for your service (no code required)
- Providing async, sync and streaming functionality.
- Neat less integration into the SOCAITY ecosystem for running ai services like python functions.
- Monitoring server state.

The code is fast, lightweight, pure python and meant to be flexible.

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
- The method will return a "Job" object instead of the result, including a job id.
- By calling the endpoint with predict?job_id=... or the "status" endpoint you can get the result / status of the job.


Note: in case of "runpod", "serverless" this is not necessary, as the job mechanism is handled by runpod deployment.

## Calling the endpoints -> Getting the job result

You can call the endpoints with a simple http request.
You can try them out in the browser, with curl or Postman. 
For more convenience with the socaity package, you can use the endpoints like functions.

## Use the endpoints like functions with the socaity package.
If you have the socaity package installed, you can use the endpoints like a function.
This makes it insanely useful for complex scenarious where you use multiple models and endpoints.
Socaity package release comes soon.

#### Async

```python
job = predict("my_param1", my_param2=2)
result = job.result(

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





# Deploying a Service to production

## Runpod
It is not required to write a handler function anymore. The socaity router magic handles it :D
Just write a simple docker file and deploy it to runpod. 


## Writing your own Router

You can also write your own router to extend the SocaityRouters capabilities.
