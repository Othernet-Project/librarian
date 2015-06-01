SQL = """
alter table zipballs add column disabled boolean not null default 0;
"""


def up(db, conf):
    db.executescript(SQL)
