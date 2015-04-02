SQL = """
alter table users add column options varchar default '{}';
"""


def up(db, config):
    db.executescript(SQL)
