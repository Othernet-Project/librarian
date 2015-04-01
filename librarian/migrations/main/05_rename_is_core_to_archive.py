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
    views integer not null default 0,
    keep_formatting boolean not null default 0,
    is_partner boolean not null default 0,
    is_sponsored boolean not null default 0,
    archive varchar not null default 'core',
    partner varchar,
    license varchar
);

replace into zipballs
(md5, domain, url, title, images, timestamp, updated, favorite, views,
    keep_formatting, is_partner, is_sponsored, partner, license)
select
md5, domain, url, title, images, timestamp, updated, favorite, views,
keep_formatting, is_partner, is_sponsored, partner, license
from tmp;

update zipballs
set archive = 'core'
where (select is_core from tmp where md5 = tmp.md5) == 1;

drop table tmp;
"""


def up(db, conf):
    db.executescript(SQL)
