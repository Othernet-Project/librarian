SQL = """
create table links
(
    source varchar not null,
    target varchar not null,
    unique(source, target)
);
"""


def up(db, conf):
    db.executescript(SQL)
