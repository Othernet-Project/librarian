SQL = """
alter table facets
  add column keywords varchar,
  add column copyright varchar,
  add column language varchar,
  add column outernet_formatting boolean;
"""


def up(db, conf):
    db.executescript(SQL)
