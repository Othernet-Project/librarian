from bottle import request

from librarian.librarian_core.contrib.auth.acl import BaseGroup

from .utils import from_csv, row_to_dict


class GroupNotFound(Exception):
    pass


class Group(BaseGroup):

    def __init__(self, db=None, *args, **kwargs):
        self.db = db or request.db.sessions
        super(Group, self).__init__(*args, **kwargs)

    @classmethod
    def from_name(cls, group_name, db=None):
        db = db or request.db.sessions
        query = db.Select(sets='groups', where='name = :name')
        db.query(query, name=group_name)
        group = db.result
        group = row_to_dict(group) if group else {}

        if group:
            group['permissions'] = from_csv(group.pop('permissions', ''))
            return cls(db=db, **group)

        raise GroupNotFound(group_name)

    def save(self):
        query = self.db.Replace('groups',
                                name=':name',
                                permissions=':permissions',
                                has_superpowers=':has_superpowers',
                                where='name = :name')
        self.db.query(query,
                      name=self.name,
                      permissions=self.permissions,
                      has_superpowers=self.has_superpowers)
