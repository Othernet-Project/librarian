SQL = """
alter table zipballs add column favorite boolean not null default 0;
alter table zipballs add column views integer not null default 0;
"""


def up(db, conf):
    db.executescript(SQL)
