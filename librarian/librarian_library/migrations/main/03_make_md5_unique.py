SQL = """
alter table zipballs rename to tmp;

create table zipballs
(
    md5 varchar primary_key unique not null,
    domain varchar not null,
    url varchar not null,
    title varchar not null,
    images integer not null default 0,
    timestamp timestamp not null,
    updated timestamp not null,
    favorite boolean not null default 0,
    views integer not null default 0
);

replace into zipballs
(md5, domain, url, title, images, timestamp, updated, favorite)
select
md5, domain, url, title, images, timestamp, updated, views
from tmp;

drop table tmp;
"""


def up(db, conf):
    db.executescript(SQL)
