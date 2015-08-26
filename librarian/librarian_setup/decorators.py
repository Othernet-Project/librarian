

AUTO_CONFIGURATORS = dict()


def autoconfigure(name):
    """Register functions that will be automatically ran in case a setup file
    was not found. The value these functions return will be associated with the
    passed in `name` parameter, and the resulting pair will be added to the
    setup data."""
    def decorator(func):
        AUTO_CONFIGURATORS[name] = func
        return func
    return decorator
