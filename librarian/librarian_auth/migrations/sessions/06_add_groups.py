SQL = """
create table groups
(
    name varchar primary_key unique not null,   -- unique group name
    permissions text,                           -- comma separated list of permissions
    has_superpowers boolean not null default 0  -- is superuser?
);
"""


def up(db, conf):
    db.executescript(SQL)
