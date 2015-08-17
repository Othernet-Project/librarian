SQL = """
create table html
(
    md5 varchar primary_key unique not null,
    keep_formatting boolean not null default 0,
    main varchar not null default 'index.html'
);

replace into html (md5, keep_formatting, main)
select md5, keep_formatting, entry_point
from zipballs;
"""


def up(db, conf):
    db.executescript(SQL)
