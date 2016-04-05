

class Task:

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    @classmethod
    def install(cls):
        # TODO: analyze existing task install implementation and come up with
        # a generic installer / rescheduler system that will be implemented
        # in this base class
        raise NotImplementedError()
