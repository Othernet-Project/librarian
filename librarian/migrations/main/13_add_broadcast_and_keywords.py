SQL = """
alter table zipballs add column broadcast date;
alter table zipballs add column keywords varchar not null default '';
"""


def up(db, conf):
    db.executescript(SQL)
