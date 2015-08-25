SQL = """
alter table zipballs rename to tmp;

create table zipballs
(
    md5 varchar primary_key unique not null,
    url varchar not null,
    title varchar not null,
    timestamp timestamp not null,
    updated timestamp not null,
    favorite boolean not null default 0,
    views integer not null default 0,
    is_partner boolean not null default 0,
    is_sponsored boolean not null default 0,
    archive varchar not null default 'core',
    publisher varchar,
    license varchar,
    tags varchar,
    language varchar,
    size integer,
    broadcast date,
    keywords varchar not null default '',
    disabled boolean not null default 0
);

replace into zipballs
(md5, url, title, timestamp, updated, favorite, views, is_partner, is_sponsored,
    archive, publisher, license, tags, language, size, broadcast, keywords,
    disabled)
select
md5, url, title, timestamp, updated, favorite, views, is_partner, is_sponsored,
archive, publisher, license, tags, language, size, broadcast, keywords, disabled
from tmp;

drop table tmp;
"""


def up(db, conf):
    db.executescript(SQL)
