SQL = """
alter table zipballs add column language varchar;
"""


def up(db, conf):
    db.executescript(SQL)
