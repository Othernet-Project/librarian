SQL = """
alter table users add column groups text;
"""


def up(db, conf):
    db.executescript(SQL)
