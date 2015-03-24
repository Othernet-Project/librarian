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
    is_partner boolean not null default 0,
    is_sponsored boolean not null default 0,
    archive varchar not null default 'core',
    partner varchar,
    license varchar,
    tags varchar,
    language varchar,
    size integer
);

replace into zipballs
(md5, url, title, images, timestamp, updated, favorite, views,
    keep_formatting, is_partner, is_sponsored, archive, partner,
    license, tags, language, size)
select
md5, url, title, images, timestamp, updated, favorite, views,
keep_formatting, is_partner, is_sponsored, archive, partner,
license, tags, language, size
from tmp;

drop table tmp;
"""


def up(db, conf):
    db.executescript(SQL)
