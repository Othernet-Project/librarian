from bottle import request

from librarian.librarian_core.contrib.auth.acl import BaseGroup

from .utils import from_csv, row_to_dict


class GroupNotFound(Exception):
    pass


class Group(BaseGroup):

    @classmethod
    def from_name(cls, group_name):
        db = request.db.sessions
        query = db.Select(sets='groups', where='name = :name')
        db.query(query, name=group_name)
        group = db.result
        group = row_to_dict(group) if group else {}

        if group:
            group['permissions'] = from_csv(group.pop('permissions', ''))
            return cls(**group)

        raise GroupNotFound(group_name)

    def save(self):
        db = request.db.sessions
        query = db.Replace('groups',
                           name=':name',
                           permissions=':permissions',
                           has_superpowers=':has_superpowers',
                           where='name = :name')
        db.query(query,
                 name=self.name,
                 permissions=self.permissions,
                 has_superpowers=self.has_superpowers)
