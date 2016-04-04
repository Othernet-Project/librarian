from ..databases.utils import from_csv, row_to_dict

from .base import BaseGroup
from .helpers import identify_database


class GroupNotFound(Exception):
    pass


class Group(BaseGroup):

    @identify_database
    def __init__(self, db, *args, **kwargs):
        self.db = db
        super(Group, self).__init__(*args, **kwargs)

    @classmethod
    @identify_database
    def from_name(cls, group_name, db):
        query = db.Select(sets='groups', where='name = %(name)s')
        group = db.fetchone(query, dict(name=group_name))
        group = row_to_dict(group) if group else {}

        if group:
            group['permissions'] = from_csv(group.pop('permissions', ''))
            return cls(db=db, **group)

        raise GroupNotFound(group_name)

    def save(self):
        query = self.db.Replace(
            'groups',
            constraints=['name'],
            cols=('name', 'permissions', 'has_superpowers'),
        )
        self.db.execute(query, dict(name=self.name,
                                    permissions=self.permissions,
                                    has_superpowers=self.has_superpowers))
