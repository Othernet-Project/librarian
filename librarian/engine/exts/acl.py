import functools

from bottle import request


def is_string(obj):
    if 'basestring' not in globals():
        basestring = str
    return isinstance(obj, basestring)


class PermissionDenied(Exception):
    """Exception being raised by helper functions if a user has no permission
    to access a resource."""
    pass


class BasePermission(object):
    name = None  # subclasses should provide a unique identifier

    def __init__(self):
        if self.name is None:
            raise ValueError("Permisson class has no `name` attribute "
                             "specified.")

    def is_granted(self):
        """The default behavior is that solely a permission object's presence
        in a group grants access. However, if special conditions need to be
        checked, subclasses may override this method and perform custom
        verifications."""
        return True

    @classmethod
    def cast(cls, name):
        for subclass in cls.__subclasses__():
            if subclass.name == name:
                return subclass

        raise ValueError("No Permission class found under the name: "
                         "{0}".format(name))


class BaseGroup(object):
    """Subclasses should provide functionality for storing group objects in the
    chosen storage backend."""
    def __init__(self, name, permissions=None, has_superpowers=False):
        """
        :param name:             string - unique group name
        :param permissions:      list of permission names that will be used to
                                 find their respective classes
        :param has_superpowers:  bool, if set, all permissions are granted
        """
        self.name = name
        self.has_superpowers = has_superpowers
        # assemble list of permission classes
        permissions = permissions or []
        self.permission_classes = [BasePermission.cast(perm)
                                   for perm in permissions]

    def contains_permission(self, permission_class):
        return permission_class in self.permission_classes

    def add_permission(self, permission_class):
        self.permission_classes.append(permission_class)

    def remove_permission(self, permission_class):
        if self.contains_permission(permission_class):
            self.permission_classes.remove(permission_class)

    @property
    def permissions(self):
        return [cls.name for cls in self.permission_classes]


class BaseUser(object):
    """Subclasses should provide functionality for storing and retrieving user
    objects in the chosen storage backend, including the list of groups that
    the user belongs to."""
    def __init__(self, groups):
        if type(self) is BaseUser:
            raise TypeError("Abstract {0} class cannot be used "
                            "directly.".format(BaseUser.__name__))
        self.groups = groups

    def has_permission(self, permission_class):
        if is_string(permission_class):
            permission_class = BasePermission.cast(permission_class)

        for group in self.groups:
            if group.has_superpowers:
                return True

            if group.contains_permission(permission_class):
                return permission_class().is_granted()

        return False


def permission_required(*permissions, user_getter=lambda: request.user,
                        denied_exception_class=PermissionDenied):
    """Decorator to protect a function from being invoked if the user that is
    trying to access it has no permission to do so. Usage:

    @permission_required(IsSecretService, IsBlessed, 'permission_name_also_ok')
    def your_func():
        return "secret"

    In case the user object is not on the request object itself, an optional
    `user_getter` parameter can specify a custom getter function which needs to
    return a user object when invoked.
    By default, if a permission is denied, the `PermissionDenied` exception
    will be raised. A custom exception class can be specified using the
    `denied_exception_class` parameter.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = user_getter()
            if all(map(user.has_permission, permissions)):
                return func(*args, **kwargs)

            if denied_exception_class:
                raise denied_exception_class()
            # deny access silently if that's what's needed
        return wrapper
    return decorator


def init_begin(supervisor):
    # routes, plugins, etc. can access this decorator through the supervisor
    # object during their installation and wrap themselves if they need to.
    supervisor.exts.permission_required = permission_required
