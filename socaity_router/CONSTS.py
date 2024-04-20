from enum import Enum
class EXECUTION_PROVIDERS(Enum):
    RUNPOD = "runpod"
    FASTAPI = "fastapi"

class EXECUTION_ENVIRONMENTS(Enum):
    LOCALHOST = "localhost"
    HOSTED = "hosted"


class SERVER_STATUS:
    INITIALIZING = "initializing"
    BOOTING = "booting"
    RUNNING = "running"
    BUSY = "busy"
    ERROR = "error"