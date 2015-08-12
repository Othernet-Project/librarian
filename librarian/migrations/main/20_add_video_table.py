SQL = """
create table video
(
    md5 varchar primary_key not null,
    main varchar not null default 'video.mp4',
    duration integer,
    resolution varchar,
    description varchar
);
"""


def up(db, conf):
    db.executescript(SQL)
