

class Task:

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    @classmethod
    def install(cls):
        raise NotImplementedError()
