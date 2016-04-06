def plugin(supervisor):
    # FIXME: Not implemented
    def noop(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return noop
