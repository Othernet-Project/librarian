SQL = """
create table permissions
(
    name varchar not null,        -- permission name as defined on the permission class
    identifier varchar not null,  -- a unique identifier to associate some other object with the permission data
    data varchar default '{}',    -- arbitary json serialized data
    unique(name, identifier)
);
"""


def up(db, conf):
    db.executescript(SQL)
