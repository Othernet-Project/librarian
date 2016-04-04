SQL = """
alter table dirinfo add column view varchar;
"""


def up(db, conf):
    db.executescript(SQL)
