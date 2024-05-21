from enum import Enum
class EXECUTION_PROVIDERS(Enum):
    RUNPOD = "runpod"
    FASTAPI = "fastapi"

class EXECUTION_ENVIRONMENTS(Enum):
    LOCALHOST = "localhost"
    HOSTED = "hosted"
    SERVERLESS = "serverless"

class SERVER_STATUS(Enum):
    INITIALIZING = "initializing"
    BOOTING = "booting"
    RUNNING = "running"
    BUSY = "busy"
    ERROR = "error"