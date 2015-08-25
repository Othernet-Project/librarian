SQL = """
create table generic
(
    md5 varchar primary_key unique not null,
    description varchar
);
"""


def up(db, conf):
    db.executescript(SQL)
