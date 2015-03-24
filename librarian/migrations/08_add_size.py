SQL = """
alter table zipballs add column size integer;
"""


def up(db, conf):
    db.execute(SQL)
