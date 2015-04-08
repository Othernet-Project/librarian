SQL = """
alter table zipballs add column multipage boolean not null default 0;
alter table zipballs add column entry_point varchar not null default 'index.html';
"""


def up(db, conf):
    db.executescript(SQL)
