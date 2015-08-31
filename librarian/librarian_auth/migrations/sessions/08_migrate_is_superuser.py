SQL_MIGRATE = """
alter table users rename to tmp;

create table users
(
    username varchar primary_key unique not null,
    password varchar not null,
    created timestamp not null,
    options varchar default '{}',
    reset_token text,
    groups text
);

replace into users
(username, password, created, options, reset_token)
select
username, password, created, options, reset_token
from tmp;
"""

SQL_CREATE_GROUP = """
INSERT INTO groups (name, permissions, has_superpowers)
VALUES ('superuser', '', 1);
"""

SQL_GET_SUPERUSERS = """
select * from tmp where is_superuser = 1;
"""

SQL_ASSIGN_SUPERUSER_GROUP = """
UPDATE users
SET groups = 'superuser'
WHERE username = '{0}';
"""

SQL_CLEANUP = """
drop table tmp;
"""


def up(db, conf):
    db.executescript(SQL_MIGRATE)
    # create superusers group
    db.execute(SQL_CREATE_GROUP)
    # get list of superusers
    db.execute(SQL_GET_SUPERUSERS)

    superusers = db.results
    for user in superusers:
        sql_upd = SQL_ASSIGN_SUPERUSER_GROUP.format(user.username)
        db.execute(sql_upd)

    db.execute(SQL_CLEANUP)
