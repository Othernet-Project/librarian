SQL = """
alter table users add column reset_token text;
"""


def up(db, conf):
    db.executescript(SQL)
