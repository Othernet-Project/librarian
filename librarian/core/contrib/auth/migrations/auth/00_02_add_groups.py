SQL = """
create table groups
(
    name varchar primary key,                       -- unique group name
    permissions text,                               -- comma separated list of permissions
    has_superpowers boolean not null default false  -- is superuser?
);
"""

SQL_CREATE_GROUP = """
INSERT INTO groups (name, permissions, has_superpowers)
VALUES ('superuser', '', true);
"""


def up(db, conf):
    db.executescript(SQL)
    # create superusers group
    db.execute(SQL_CREATE_GROUP)
