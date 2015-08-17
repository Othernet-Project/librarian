SQL = """
create table app
(
    md5 varchar primary_key unique not null,
    version varchar,
    description varchar
);
"""


def up(db, conf):
    db.executescript(SQL)
