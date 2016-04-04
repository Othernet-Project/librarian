SQL = """
alter table dirinfo add column cover varchar;
alter table dirinfo add column publisher varchar;
alter table dirinfo add column keywords varchar;
"""


def up(db, conf):
    db.executescript(SQL)
