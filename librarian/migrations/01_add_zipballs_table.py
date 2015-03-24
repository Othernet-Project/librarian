SQL = """
create table zipballs
(
    md5 varchar primary_key not null,   -- md5 of the URL
    domain varchar not null,            -- domain name
    url varchar not null,               -- original URL
    title varchar not null,             -- page title
    images integer not null default 0,  -- number of images
    timestamp timestamp not null,       -- timestamp as stated in metadata
    updated timestamp not null          -- update timestamp
);
"""


def up(db, conf):
    db.executescript(SQL)
