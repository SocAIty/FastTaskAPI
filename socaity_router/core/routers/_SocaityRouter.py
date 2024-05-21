from socaity_router.CONSTS import SERVER_STATUS


class _SocaityRouter:
    """
    Base class for all routers.
    """
    def __init__(self, *args, **kwargs):
        self.status = SERVER_STATUS.INITIALIZING
        self.add_route(path="/status")(self.get_status)
        self.add_route(path="/job")(self.get_job)

    def get_status(self) -> SERVER_STATUS:
        return self.status

    def get_job(self, job_id: str):
        raise NotImplementedError("Implement in subclass")

    def start(self):
        raise NotImplementedError("Implement in subclass")

    def add_route(
            self,
            path: str = None,
            queue_size: int = 100,
            *args,
            **kwargs
    ):
        """
        Adds an additional wrapper to the API path functionality.
        """
        raise NotImplementedError("Implement in subclass")

    def get(self, path: str = None, queue_size: int = 1):
        raise NotImplementedError("Implement in subclass")
