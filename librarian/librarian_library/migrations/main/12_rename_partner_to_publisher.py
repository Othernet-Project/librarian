SQL = """
alter table zipballs rename to tmp;

create table zipballs
(
    md5 varchar primary_key unique not null,
    url varchar not null,
    title varchar not null,
    images integer not null default 0,
    timestamp timestamp not null,
    updated timestamp not null,
    favorite boolean not null default 0,
    views integer not null default 0,
    keep_formatting boolean not null default 0,
    is_publisher boolean not null default 0,
    is_sponsored boolean not null default 0,
    archive varchar not null default 'core',
    publisher varchar,
    license varchar,
    tags varchar,
    language varchar,
    size integer,
    multipage boolean not null default 0,
    entry_point varchar not null default 'index.html'
);

replace into zipballs
(md5, url, title, images, timestamp, updated, favorite, views, keep_formatting,
    is_publisher, is_sponsored, archive, publisher, license, tags, language,
    size, multipage, entry_point)
select
md5, url, title, images, timestamp, updated, favorite, views, keep_formatting,
    is_partner, is_sponsored, archive, partner, license, tags, language,
    size, multipage, entry_point
from tmp;

drop table tmp;
"""


def up(db, conf):
    db.executescript(SQL)
