SQL = """
create table image
(
    md5 varchar primary_key not null,
    description varchar
);

create table album
(
    md5 varchar primary_key not null,
    file varchar,
    thumbnail varchar,
    caption varchar,
    title varchar,
    resolution varchar
);
"""


def up(db, conf):
    db.executescript(SQL)
