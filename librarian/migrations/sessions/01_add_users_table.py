SQL = """
create table users
(
    username varchar primary_key unique not null,   -- username
    password varchar not null,                      -- encrypted password
    is_superuser boolean not null default 0,        -- is admin user
    created timestamp not null                      -- user creation timestamp
);
"""


def up(db, conf):
    db.executescript(SQL)
