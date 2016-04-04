SQL = """
alter table facets
  add column facet_types smallint default 1 -- generic
"""


def up(db, conf):
    db.executescript(SQL)
