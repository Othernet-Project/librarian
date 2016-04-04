SQL = """
create table dirinfo
(
    path varchar not null,
    language varchar,
    name varchar,
    description varchar,
    icon varchar,
    unique(path, language)
);
"""


def up(db, conf):
    db.executescript(SQL)
