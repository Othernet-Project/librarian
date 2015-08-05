SQL = """
create table audio
(
    md5 varchar primary_key not null,
    description varchar
);

create table tracks
(
    md5 varchar primary_key not null,
    file varchar,
    title varchar,
    duration integer
);
"""


def up(db, conf):
    db.executescript(SQL)
