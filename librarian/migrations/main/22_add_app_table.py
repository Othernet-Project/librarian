SQL = """
create table app
(
    md5 varchar primary_key not null,
    version varchar
);
"""


def up(db, conf):
    db.executescript(SQL)
