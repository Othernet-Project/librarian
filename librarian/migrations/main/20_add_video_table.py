SQL = """
create table video
(
    md5 varchar primary_key not null,
    duration integer,
    resolution varchar
);
"""


def up(db, conf):
    db.executescript(SQL)
