SQL = """
alter table zipballs add column content_type int not null default 1;
"""


def up(db, conf):
    db.executescript(SQL)
