SQL = """
create table video
(
    md5 varchar primary_key not null,
    file varchar,
    duration integer,
    resolution varchar,
    description varchar
);
"""


def up(db, conf):
    db.executescript(SQL)
