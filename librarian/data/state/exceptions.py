

class BadAccessMethod(Exception):
    """
    Raised when a storage provider doesn't support the requested access method.
    """
    pass


class AccessPermissionDenied(Exception):
    """
    Raised when a storage provider denies access to a read or write operation.
    """
    pass
