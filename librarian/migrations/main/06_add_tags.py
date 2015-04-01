SQL = """
create table tags
(
    tag_id integer primary key asc,
    name varchar not null unique on conflict ignore
);

create table taggings
(
    tag_id integer,
    md5 varchar,
    unique (tag_id, md5) on conflict ignore
);

-- Add a column that will hold cached tag values
alter table zipballs add column tags varchar;
"""


def up(db, conf):
    db.executescript(SQL)
