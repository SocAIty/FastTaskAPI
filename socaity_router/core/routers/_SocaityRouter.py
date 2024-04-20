from socaity_router.CONSTS import SERVER_STATUS

class _SocaityRouter:
    """
    Base class for all routers.
    """
    def __init__(self):
        self.status = SERVER_STATUS.INITIALIZING
        # add the get_status function to the routes
        # self.add_api_route(path="/status")(self.get_status)

    def get_status(self) -> SERVER_STATUS:
        return self.status

    def start(self):
        raise NotImplementedError("Implement in subclass")

    #def start_func(self, *args, **kwargs):
    #    """Decorator for subclasses to use like @start_func"""
    #    def wrapper(s_func):
    #        self.status = SERVER_STATUS.BOOTING
    #        s_func(*args, **kwargs)
    #        self.status = SERVER_STATUS.RUNNING
    #    return wrapper
#
    #def start_func_serverless(self, *args, **kwargs):
    #    """Decorator for subclasses to use like @start_func_serverless"""
    #    def wrapper(s_func):
    #        self.status = SERVER_STATUS.BOOTING
    #        s_func(*args, **kwargs)
    #        self.status = SERVER_STATUS.RUNNING
#
    #    return wrapper

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
