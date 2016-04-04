SQL = """
create table facets
(
    path varchar not null,
    file varchar not null,
    author varchar default '',
    description varchar default '',
    title varchar default '',
    genre varchar default '',
    album varchar default '',
    width int default 0,
    height int default 0,
    duration int default 0,
    unique(path, file)
);
"""


def up(db, conf):
    db.executescript(SQL)
