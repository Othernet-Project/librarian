SQL = """
create table fs
(
    id serial primary key,
    parent_id integer not null default 0,
    path varchar unique not null,
    type smallint not null,
    content_types smallint not null default 1 -- generic
);
create unique index on fs (path);
create index on fs (path, content_types);
create table meta
(
    id serial primary key,
    fs_id integer references fs (id),
    language varchar,
    key varchar,
    value varchar,
    unique (fs_id, language, key)
);
"""


def up(db, conf):
    db.executescript(SQL)
