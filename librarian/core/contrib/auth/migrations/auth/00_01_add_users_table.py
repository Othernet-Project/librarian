SQL = """
create table users
(
    username varchar primary key,             -- username, case insensitive
    password varchar not null,                -- encrypted password
    created timestamptz not null,             -- user creation timestamp
    options varchar default '{}',             -- arbitary user options in json
    reset_token text,                         -- password reset token
    groups text                               -- comma separated list of groups
);
"""


def up(db, conf):
    db.executescript(SQL)
