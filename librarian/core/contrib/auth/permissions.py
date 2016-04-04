import functools
import json

from ...utils import is_string
from ..databases.serializers import DateTimeDecoder, DateTimeEncoder

from .base import BasePermission
from .helpers import identify_database


class BaseDynamicPermission(BasePermission):

    @identify_database
    def __init__(self, identifier, db):
        super(BaseDynamicPermission, self).__init__()
        self.db = db
        self.identifier = identifier
        self.data = self._load()

    def _load(self):
        q = self.db.Select(
            sets='permissions',
            where='name = %(name)s AND identifier = %(identifier)s'
        )
        result = self.db.fetchone(q, dict(name=self.name,
                                          identifier=self.identifier))
        if result:
            return json.loads(result['data'], cls=DateTimeDecoder)
        return {}

    def save(self):
        q = self.db.Replace('permissions',
                            constraints=('name', 'identifier'),
                            cols=('name', 'identifier', 'data'))
        data = json.dumps(self.data, cls=DateTimeEncoder)
        self.db.execute(q, dict(name=self.name,
                                identifier=self.identifier,
                                data=data))


class ACLPermission(BaseDynamicPermission):
    name = 'acl'

    NO_PERMISSION = 0
    READ = 4
    WRITE = 2
    EXECUTE = 1
    ALIASES = {
        'r': READ,
        'w': WRITE,
        'x': EXECUTE,
        READ: READ,
        WRITE: WRITE,
        EXECUTE: EXECUTE
    }
    VALID_BITMASKS = range(1, 8)

    def to_bitmask(func):
        @functools.wraps(func)
        def wrapper(self, path, permission):
            if is_string(permission):
                try:
                    bitmask = sum([self.ALIASES[p] for p in list(permission)])
                except KeyError:
                    msg = "Invalid permission: {0}".format(permission)
                    raise ValueError(msg)
            else:
                bitmask = permission

            if bitmask not in self.VALID_BITMASKS:
                msg = "Invalid permission: {0}".format(permission)
                raise ValueError(msg)

            return func(self, path, bitmask)
        return wrapper

    @to_bitmask
    def grant(self, path, permission):
        existing = self.data.get(path, self.NO_PERMISSION)
        self.data[path] = existing | permission
        self.save()

    @to_bitmask
    def revoke(self, path, permission):
        existing = self.data.get(path, self.NO_PERMISSION)
        permission = existing & ~permission
        if permission == self.NO_PERMISSION:
            # when having no permission, we can freely just remove the whole
            # path as not having a path at all also means having no permissions
            # whatsoever
            self.data.pop(path, None)
        else:
            self.data[path] = permission

        self.save()

    def clear(self):
        self.data = {}
        self.save()

    @to_bitmask
    def is_granted(self, path, permission):
        existing = self.data.get(path, self.NO_PERMISSION)
        return existing & permission == permission
