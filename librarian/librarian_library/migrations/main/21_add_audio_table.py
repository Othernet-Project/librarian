SQL = """
create table audio
(
    md5 varchar primary_key unique not null,
    description varchar
);

create table playlist
(
    md5 varchar primary_key not null,
    file varchar,
    title varchar,
    duration integer,
    unique(md5, file) on conflict replace
);
"""


def up(db, conf):
    db.executescript(SQL)
